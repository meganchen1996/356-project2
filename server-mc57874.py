import sys
import time
import collections
import ipaddress
from socket import *

clientPort = 6930

#routing table 
routing_table = collections.OrderedDict();

#routing table engine server

#longest prefix match rule (longer prefix wins) assuming they are equal or lesser cost.
#ex. a /16 that matches is overriden by a /24 that matches, but if the /24 is more expensive, 
# your table should still prefer the /16

#set up of server
def run_server():
	serverSocket = socket(AF_INET, SOCK_STREAM)
	serverPort = int(sys.argv[1])
	serverSocket.bind(('',serverPort))
	serverSocket.listen(1)

	while 1:
		clientSocket, port = serverSocket.accept()
		rawMessage = clientSocket.recv(2048)
		response = parse_request(rawMessage.decode()); #decoding it so that you can parse to find real http headers
		clientSocket.send(response.encode())
	serverSocket.close()

#error handling

#sends back the status, will do error checking all up in run_server
def parse_request(message):
	lines = message.split('\r\n') # collection of lines in the request
	command = lines[0]
	if(command == 'UPDATE'):
		return update(lines)
	if(command == 'QUERY'):
		return query(lines)
	else:
		return 'NOTHING'

#construct response
#headers you need: server, date, content-type, content-length, last-modified
def generate_response(command):
	tnow = time.gmtime()
	tnowstr = time.strftime('%a, %d %b %Y %H:%M:%S %Z', tnow)
	response = ''
	return response


#update - receive messages updating routing information
#Example request for an UPDATE command
# UPDATE <cr><lf>
# A<sp>200.34.55.0/24<sp>22<cr><lf>
# A<sp>200.34.56.0/24<sp>22<cr><lf>
# B<sp>200.34.54.0/24<sp>35<cr><lf>
# C<sp>200.34.0.0/16<sp>41<cr><lf>
# END<cr><lf
def update(body):
	# check the table to see if the advertised path receieved is better than the one stored
	# if it is better, then update it
	# call generate response
	i = 1;
	while(body[i] != 'END'):
		body_request = body[i].split(' ')
		router = body_request[0]
		subnet = body_request[1]
		cost = body_request[2]
		#check if it already exists and if it's more expensive
		key = router + ' ' + subnet;
		if(key in routing_table):
			if (routing_table[key] <= cost):
				routing_table[key] = cost
		#else just add it in
		else:
			routing_table[key] = cost
		i+=1

	response = 'ACK\r\nEND\r\n'
	return response

#query - receive questions asking server where it would route a message (where to forward packets)
def query(body):
	#get ip address
	ip = body[1]
	#iterate through to check if the ip is within a subnet
	for key, cost in routing_table.items():
		key_split = key.split(' ')
		router = key[0]
		subnet = key[1]
		if(ipaddress.ip_address(ip) in ipaddress.ip_network(subnet)):
			response = 'RESULT\r\n' + ip + ' ' + router + ' ' + cost + '\r\n' + 'END\r\n'
			return response
	return 'QUERY'

def subnet_is_better(best, new):
	if()
run_server()
