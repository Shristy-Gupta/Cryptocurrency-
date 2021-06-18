# Cryptocurrency-
Cryptocurrency with three users and in distributed network
Three nodes:

http://127.0.0.1:5001/

http://127.0.0.1:5002/

http://127.0.0.1:5003/

GET Requests:
mine_block: Mines the new block
get_chain: Returns the all the blocks attached to a perticular node
is_valid: If the current mined block is valid
replace_chain: Replacing the chain with the longest chain if needed in a decentralized network



POST Requests:
add_transaction: Adds the transaction to the newest block. Uses transaction.json in POST request
connect_node: Connect the node with other nodes in the decentralized network. Use nodes.json in POST request


Some snippets from Postman
![image](https://user-images.githubusercontent.com/26459890/122520353-1e952d80-d031-11eb-9048-035747bb5608.png)
![image](https://user-images.githubusercontent.com/26459890/122520419-32409400-d031-11eb-9a3c-dc1ef28bf094.png)


