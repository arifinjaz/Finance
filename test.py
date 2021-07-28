from helpers import apology, login_required, lookup, usd, validate
import flask_login

help(flask_login)

share = lookup('KXIN')
qty = 2

#print (share["name"])
#for sh in share:
#    print(share[sh])

test = [{'QTY': 12, 'PRICE': 1.54, 'SHARESYMBOL': 'IDEX', 'SHARE': 'Ideanomics, Inc.'}, {'QTY': 3, 'PRICE': 16.666666666666668, 'SHARESYMBOL': 'KXIN', 'SHARE': 'Kaixin Auto Holdings'}, {'QTY': 1, 'PRICE': 488.24, 'SHARESYMBOL': 'NFLX', 'SHARE': 'Netflix, Inc.'}]

tes = [{'SHARESYMBOL': 'KXIN'}, {'SHARESYMBOL': 'IDEX'}, {'SHARESYMBOL': 'NFLX'}]

amount=[]
#for d in test:
 #   amount.append(usd(d["PRICE"]))
#print(amount)

for te in test:
    te["PRICE"]=usd(te["PRICE"])
    #print(te["QTY"],te["PRICE"],te["SHARESYMBOL"],te["SHARE"])
#print(share)
#tamount = (share["price"] * qty)
#print (share)
password = 'Aesttest12!'
validate(password)

special_characters = "!@#$%^&*()-+?_=,<>/"
print (special_characters)