import pandas as pd
import random
#movies = pd.read_csv("movies.csv",encoding="Latin1")
Ratings = pd.read_csv("ratings.csv")

def getmatrix(Ratings):

	final=pd.pivot_table(Ratings,values='rating',index='userId',columns='movieId')

	#print(final)
	final=final.fillna(final.mean(axis=0))
	#print(final)
	corr=final.transpose()
	corr_final=corr.corr(method='pearson')
	return final,corr_final

def Top_N(userID,corr_matrix):
    user = userID
    corr_final = corr_matrix
    res = corr_final.iloc[user-1]
    final_res=dict()
    for x in range(len(res)):
        final_res[res.iloc[x]]=x+1
    res = sorted(list(res))
    res_=[]
    for x in range(1,30):
        res_.append(res[len(res)-(x+1)])
    return final_res,res_
        #print(res[len(res)-(x+1)])

def calculate_rating(final,final_res,res_,user,movie):
    corr_sum=0
    pi_pm=0
    movie=movie
    user=user
    for x in range(15):
        temp=final.loc[final_res[res_[x]]]
        #print(temp.mean(axis=0))
        #print(final.loc[final_res[res_[x]],movie])
        corr_sum+=res_[x]
        #t = final.loc[final_res[res_[x]],movie] - temp.mean(axis=0)
        t = final.loc[final_res[res_[x]],movie]*res_[x]
        pi_pm+=t
        t=0

    mu_rating = final.loc[user]
    mu_rating = mu_rating.mean(axis=0)

    grand_rating =  (pi_pm/corr_sum)
    return grand_rating

class x:
	
	userid_dict=dict
	userTop_n=[]
	def __init__(self,u,u1,u2):
		self.userid=u
		self.userid_dict=u1
		self.userTop_n=u2

g=[]
def evaluate(final_matrix,corr_matrix,userID,movieID):
	set=False
	userid_dict=None
	userTop_n=None
	for i in g:
		if i.userid==userID:
#			print("exists "+str(userID))
			set=True
			userid_dict=i.userid_dict
			userTop_n=i.userTop_n
	if set==False:
		userid_dict,userTop_n=Top_N(userID,corr_matrix)
		g.append(x(userID,userid_dict,userTop_n))
	res_final=calculate_rating(final_matrix,userid_dict,userTop_n,userID,movieID)
	return res_final
   
   

