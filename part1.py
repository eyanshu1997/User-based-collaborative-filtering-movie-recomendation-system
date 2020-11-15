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
    
def genfolds(Ratings):
#	print(len(Ratings))
	chunk=len(Ratings)//5
	folds=[]
	indexes=list(Ratings.index.values)
	overall=set()
	for i in range(4):
		testchunk=set()
		while(len(testchunk)!=chunk):
			val=random.randint(0,len(indexes)-1)
			if indexes[val] not in overall:
				testchunk.add(indexes[val])
				overall.add(indexes[val])
		testchunk=list(testchunk)
		testratings=Ratings.iloc[testchunk]
		folds.append(testratings)
	trainratings=Ratings.drop(overall,axis=0)
	folds.append(trainratings)
#	print(testratings)
#	print(trainratings)
	#print(testchunk)
#	print(folds)
	return folds

def MAE():
	folds=genfolds(Ratings)
	overall=0	
	ocount=0
	for i in range(5):
		test=folds[i]
		train=Ratings.drop(list(test.index.values),axis=0)
		train_fr,corr=getmatrix(train)
#		print(train)
#		print(train_fr)
#		print(corr)
		
		mae_sum=0
		count=0
		
		for val in list(test.index.values):
			if test.loc[val,'userId'] in corr.index and test.loc[val,'movieId'] in train_fr.columns:
#					print("For user ID: "+str(test.loc[val,'userId'])+" Movie ID: "+str(test.loc[val,'movieId'])+" Actual Rating: "+str(test.loc[val,'rating']))
					re=evaluate(train_fr,corr,int(test.loc[val,'userId']),int(test.loc[val,'movieId']))
#					print("For user ID: "+str(test.loc[val,'userId'])+" Movie ID: "+str(test.loc[val,'movieId'])+" Predicted Rating: "+str(re))
					mae_sum+=abs(test.loc[val,'rating'] - re)
					count+=1
		print("After one iteration without changing Top_N Mean absolute Error :"+str(mae_sum/count))
		overall+=mae_sum
		ocount+=count
	print("Overall without changing Top_N Mean absolute Error :"+str(overall/ocount))
	
#userid_dict,userTop_n=Top_N(52,64620,corr_final)
#print(calculate_rating(final,userid_dict,userTop_n,52,64620))
#print(evaluate(final,corr_final,1,1208))
MAE()

	
