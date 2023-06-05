from ryu.ofproto import ofproto_v1_3
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, set_ev_cls
import subprocess
from scapy.contrib import gtp
from scapy.layers.inet import IP, UDP
from scapy.layers.l2 import Ether
from scapy.layers.dns import DNS
from copy import deepcopy
# =================================================================================================================================
# Build switch flows
commands = [
	#Normal Switching
	'sudo ovs-ofctl -O OpenFlow13 add-flow br0 "table=0,cookie=0x0,priority=100,actions=normal"',
	#Capture GTP Traffic
	'sudo ovs-ofctl -O OpenFlow13 add-flow br0 "table=0,cookie=0x1,priority=1000,udp,tp_dst=2152,actions=controller"',
	#Capture DNS Responses from Edge DNS Server
	'sudo ovs-ofctl -O OpenFlow13 add-flow br0 "table=0,cookie=0x2,priority=1000,nw_src=10.102.211.201,udp,tp_src=53,actions=controller"'
	]
for i,command in enumerate(commands):
	try:
		output = subprocess.check_output(command, shell=True)
		print(output.decode())
		print("Flow {} of {} added".format(i+1,len(commands)))
	except subprocess.CalledProcessError as e:
		print(f"Error: {e}")
# =================================================================================================================================
# Controller definition
class L2Switch(app_manager.RyuApp):
	OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

	def __init__(self, *args, **kwargs):
		super(L2Switch, self).__init__(*args, **kwargs)
		self.UE_TUNS = {}	#dict of dicts -- key = UE IP, val = dict { 0 (DL) or 1 (UL) : TEID  }
		self.QUERIES = {}	#dict of dict of dicts -- key = UDP source port making the request, val = { DNS transaction id : {"ue" : UE_IP, "dns" : server IP } }

	def learnTEID(self, ue, tuntype, teid):
		# Learn TEID & type for a particular UE
		if ue not in self.UE_TUNS.keys():		#If this is the first time seeing this UE address
			self.UE_TUNS[ue] = {}
		self.UE_TUNS[ue][tuntype] = teid 	#Save tunnel params
		print("Learned UE {}: {} teid {}".format(ue,"DL" if tuntype==0 else "UL",teid))

	def storeQuery(self, sp, txnum, ue, dns):
		# Save DNS query to match subsequent response
		self.QUERIES[sp] = { txnum :  { "ue" : ue, "dns" : dns } }
		print("Redirecting DNS query from {}:{} --> {}:53, Transaction ID {}".format(ue, sp, dns, txnum))

	def popQuery(self, sp, txnum):
		# Remove query when response comes in
		print("Redirecting DNS response for {}:53 --> {}:{}, Transaction ID {}".format(self.QUERIES[sp][txnum]["dns"], self.QUERIES[sp][txnum]["ue"], sp, txnum))
		return self.QUERIES[sp].pop(txnum)

	# Parse Openflow packet received
	@set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
	def packet_in_handler(self, ev):
		msg = ev.msg
		dp = msg.datapath
		ofp = dp.ofproto
		ofp_parser = dp.ofproto_parser

#		print(msg.data)
#		print(msg.data.hex())
		#msg.data has the entire frame from the wire,
		redir = False

		#Split up the packet into layers
		l2 = Ether(msg.data)		#Layer 2 frame
		l3 = l2.payload			#Layer 3 packet
		l4 = l3.payload			#Layer 4 datagram

		#Check if OPF packet contains GTP or DNS (or other, i guess?)
		if l4.sport == 2152 and l4.dport == 2152:
			#GTP-U traffic
			print("GTP-U traffic received")

			g = gtp.GTP_U_Header(bytes(l4.payload))		#extract GTP-U PDU

			#Verify type & extension header
			if g.gtp_type == 0xff and g.next_ex == 0x85:
				gscon = g.payload				#extract GTP PDU Session Container extension header

				if gscon.NextExtHdr == 0:
					inner_i = gscon.payload			#extract inner IP packet

					#----------------------------- UE LEARNING -----------------------------
					if gscon.type == 0:		#Downlink tunnel, UPF --> UE
						ue_ip = inner_i.dst
					if gscon.type == 1:		#Uplink tunnel, UE --> UPF
						ue_ip = inner_i.src

					known = False
					if ue_ip in self.UE_TUNS.keys():
						if gscon.type in self.UE_TUNS[ue_ip].keys():
							print("Tunnel known")
							known = True
					if not known:
						self.learnTEID(ue_ip, gscon.type, g.teid)
					#-----------------------------------------------------------------------

					#Only proceed if Downlink tunnel known (to send the DNS response back)
					proceed = False
					if 0 in self.UE_TUNS[ue_ip].keys():
						proceed = True
					if proceed:
						#Verify UDP
						if inner_i.proto == 17:
							inner_u = inner_i.payload		#extract inner UDP datagram
							
							#Verify DNS
							if  inner_u.dport == 53:
								d = DNS(bytes(inner_u.payload))	#extract DNS params

								if d.qr == 0:
									#If query -- Build a new frame for it and send to the Edge DNS server
									print("DNS query received")

									self.storeQuery(inner_u.sport,  d.id, inner_i.src, inner_i.dst) 
						
									qry_eth = Ether(
										dst='00:0c:29:88:6c:51',	#Set to MAC address of DNS server
										src='00:0c:29:a3:60:14',	#Set to MAC address of gNB
										type=0x800
									)
									qry_ip = IP(
										dst='10.102.211.201',		#Set to IP address of DNS server
										src='10.102.211.66',		#Set to IP address of gNB
										proto=17
									)
									qry_udp = UDP(
										sport=inner_u.sport,
										dport=inner_u.dport
									)
									#Construct the outgoing frame
									sfm = qry_eth / qry_ip / qry_udp / d	#Create a scapy frame
									redir = True
		elif l4.sport == 53:
			#DNS traffic
			print("DNS traffic received")

			d = DNS(bytes(l4.payload))	#extract DNS params
			if d.qr == 1:
				#If response -- build IP packet, set dst IP to UE that sent the query, encap with GTP-U (DL), finish building the frame, and send to gNB
				print("DNS response received")

				qry = self.popQuery(l4.dport, d.id)		#Get saved DNS params related to the query that triggered this response
				
				ans_outeth = Ether(
					dst='00:0c:29:a3:60:14',	#Set to MAC address of gNB
					src='00:0c:29:2d:b6:cd',	#Set to MAC address of UPF
					type=0x800
				)
				ans_outip = IP(
					dst='10.102.211.66',		#Set to IP address of gNB
					src='192.168.233.4',		#Set to IP address of UPF
					proto=17
				)
				ans_outudp = UDP(
					sport=2152,
					dport=2152
				)
				ans_g = gtp.GTP_U_Header(
					E=1,
					teid=self.UE_TUNS[qry["ue"]][0],		#This is not the same both ways, UL & DL have their own teid
					gtp_type=0xff,
					next_ex=0x85
				)
				ans_gscon = gtp.GTPPDUSessionContainer(
					QFI=1			#Scapy default seems to match the other params based on traffic we looked at
				)
				ans_inip = IP(
					dst=qry["ue"],			#Needs to be IP address of requesting UE
					src=qry["dns"],		#Set to IP address of DNS server in original request
					proto=17
				)
				ans_inudp = UDP(
					sport=l3.sport,
					dport=l3.dport
				)
				#Construct the outgoing frame
				sfm = ans_outeth / ans_outip / ans_outudp / ans_g / ans_gscon / ans_inip / ans_inudp / d		#Create a scapy frame
				redir = True

		# Send the frame out the switch
		out_port = ofproto_v1_3.OFPP_NORMAL
		actions = [ofp_parser.OFPActionOutput(out_port)]
		if redir:		#If redirecting the packet, convert scapy frame to raw bytes
			outfm = bytes(sfm)
		else:			#If no redirection, passthrough original frame
			outfm = msg.data
		out = ofp_parser.OFPPacketOut(
			datapath=dp,
			buffer_id=ofp.OFP_NO_BUFFER,
			in_port=ofp.OFPP_CONTROLLER,
			actions=actions,
			data=outfm,
			)
		dp.send_msg(out)
		print("Packet processed")