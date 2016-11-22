import sys
import ipaddress
from socket import *

clientPort = 6930

#routing table 
routing_table = dict();

#set up of server
def run_server():
	serverSocket = socket(AF_INET, SOCK_STREAM)
	serverPort = int(sys.argv[1])
	serverSocket.bind(('',serverPort))
	serverSocket.listen(1)

	#initialize routing_table
	#key: subnet
	#value: router prefix cost
	routing_table['0.0.0.0'] = "A 0 100"

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

#update - receive messages updating routing information
#Example request for an UPDATE command
# UPDATE <cr><lf>
# A<sp>200.34.55.0/24<sp>22<cr><lf>
# A<sp>200.34.56.0/24<sp>22<cr><lf>
# B<sp>200.34.54.0/24<sp>35<cr><lf>
# C<sp>200.34.0.0/16<sp>41<cr><lf>
# END<cr><lf
def update(body):
	i = 1;
	#iterate through the different requests in the body
	while(body[i] != 'END'):
		body_request = body[i].split(' ')
		req_router = body_request[0]
		req_subnet = body_request[1]
		req_prefix = (req_subnet.split('/'))[1]
		req_cost = body_request[2]

		#check if requested subnet already has an entry in the table
		if(req_subnet in routing_table):
			entry_router = (routing_table[req_subnet].split(' '))[0] 
			entry_prefix = (routing_table[req_subnet].split(' '))[1]
			entry_cost = (routing_table[req_subnet].split(' '))[2]
			#if the request is less expensive, replace with its information
			if (int(req_cost) < int(entry_cost)):
				routing_table[req_subnet] = req_router + ' ' + req_prefix + ' ' + req_cost
			#if cost is equal
			elif (int(req_cost) == int(entry_cost)):
				#check if prefix is longer or equal
				if(req_prefix_is_longer_or_equal(entry_prefix, req_prefix)):
					routing_table[req_subnet] = req_router + ' ' + req_prefix + ' ' + req_cost
			
			#if was more expensive, or cost was same but prefix was shorter, then quit out without changing

		#else doesn't exist, so just add it in
		else:
			routing_table[req_subnet] = req_router + ' ' + req_prefix + ' ' + req_cost
		i+=1

	response = 'ACK\r\nEND\r\n'
	return response

#query - receive questions asking server where it would route a message (where to forward packets)
def query(body):
	#get ip address
	ip = body[1]

	best = routing_table['0.0.0.0']; #initial 
	best_split = best.split(' ')
	best_router = best_split[0]
	best_prefix = best_split[1]
	best_cost = best_split[2]

	#iterate through to check if the ip is within a subnet
	for subnet, value in routing_table.items():
		value_split = value.split(' ')
		entry_router = value_split[0]
		entry_prefix = value_split[1]
		entry_cost = value_split[2]

		# is the ip address within the subnet?
		if(ipaddress.ip_address(ip) in ipaddress.ip_network(subnet)):
			#check if it's less expensive than the current best
			if(int(entry_cost) < int(best_cost)): 
				best = routing_table[subnet]
			elif(int(entry_cost) == int(best_cost)):
				if(req_prefix_is_longer_or_equal(best_prefix, entry_prefix)):
					best = routing_table[subnet]

			best_split = best.split(' ')
			best_router = best_split[0]
			best_prefix = best_split[1]
			best_cost = best_split[2]

	response = 'RESULT\r\n' + ip + ' ' + best_router + ' ' + best_cost + '\r\n' + 'END\r\n'
	return response;

def req_prefix_is_longer_or_equal(entry, req):
	if(int(req) >= int(entry)):
		return True;
	return False;

run_server()
