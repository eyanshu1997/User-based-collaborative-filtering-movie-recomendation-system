import pandas as pd
import random
import argparse
import numpy as np

totalcount=0
parser = argparse.ArgumentParser()
parser.add_argument('--input',help='enter the input')
parser.add_argument('--output',help="enter the output location")
args=parser.parse_args()
#print(args)	
if args.input==None or args.output==None:
	print("wrongs args")
	exit()

#movies = pd.read_csv("movies.csv",encoding="Latin1")
Ratings = pd.read_csv(args.input)
read_rating = pd.read_csv('movies.csv')




um_withnan=pd.pivot_table(Ratings,values='rating',index='userId',columns='movieId')
um_i=((um_withnan*0)+1)
um_c=um_i.fillna(0)


genre=set()
for x in range(9742):
    val=read_rating.iloc[x,2]
    val=val.split("|")
#    print(val)
    [genre.add(y) for y in val]

genre_mov=dict()
id_list=[]
genre_mov[""]=[]

ratmat=pd.pivot_table(Ratings,values='rating',index='userId',columns='movieId')
for g in genre:
    genre_mov[g]=[]
    
for x in range(9742):
    id_ = read_rating.iloc[x,0]
    val=read_rating.iloc[x,2]
    val=val.split("|")
    #print(val)
    for v in val:
        l_val=genre_mov[v]
        l_val.append(id_)
        genre_mov[v]=l_val
       
       
def find_genre(id_):
	all_genre=[]
	for x in genre:
		if id_ in genre_mov[x]:
			all_genre.append(x)
	return all_genre   
	 
def genre_corelation(genre,df):
	genrecorr={}
#	print(df)
	df_trans=df.transpose()
#	print(df_trans.loc[6849])
#	print(df_trans)
	for x in genre:
#		print(x)
		#print(genre_mov[x])
		y=[]
		for a in genre_mov[x]:
			if a in df_trans.index:
				y.append(a)
		children=df_trans.loc[y]
		final_children=children.dropna(axis=1,how="all")
		genrecorr[x]=final_children
	return genrecorr
	
def getmatrix(ratings):
	fin=pd.pivot_table(Ratings,values='rating',index='userId',columns='movieId')
#	print(final.loc[:,1])
	Ratmat=fin
	y=genre_corelation(genre,final)
	fi={}
	for x in y:
		

	#print(final)
		z=y[x].fillna(y[x].mean(axis=0))
	#print(final)
		corr=z.transpose()
		corr_final=corr.corr(method='pearson')
		fi[x]=[y[x],corr_final]
	return fin,fi


        
def common(user1,user2):
    return um_c.loc[user1].dot(um_c.loc[user2])

def top(user,corr):
	res=corr.loc[user]
#	print(res)
	final_res=dict()
	for x in range(len(res)):
		final_res[res.iloc[x]]=x+1
	res=sorted(list(res),reverse=True)
	re=[]
	for x in range(len(res)):
		if(final_res[res[x]]!=user):
			re.append((final_res[res[x]],res[x]))
	return re

def calculate_rating(fin,final,res,user,movie):
    corr_sum=0
    pi_pm=0
    movie=movie
    user=user
    wt=0
    x=0
    y=0
    while y<15 and x<len(res):
        if res[x][0] in final.index and res[x][0] in um_withnan.index:
            if not (np.isnan(fin.loc[res[x][0],movie])):
                if not (np.isnan(um_withnan.loc[res[x][0],movie])):
                    wt=common(user,res[x][0])
                    if wt==0:
                        wt=1
                    corr_sum+=(wt*res[x][1])
                #t = final.loc[final_res[res_[x]],movie] - temp.mean(axis=0)
                    t = final.loc[res[x][0],movie]*(wt*res[x][1])
                    wt=0
        x=x+1

    mu_rating = final.loc[user]
    mu_rating = mu_rating.mean(axis=0)
    return pi_pm,corr_sum

g=[]
def evaluate(fin,tr,userID,movieID):
	set=False
	usertop_n=None
	genres=find_genre(movieID)
	ta=0
	tb=0
	for gen in genres:
		if userID in tr[gen][1].index and movieID in tr[gen][0].columns:
			for i in g:
				if i[0]==gen and i[1][0]==userID:
		#			print("exists "+str(userID))
					set=True
					usertop_n=i[1][1]
					break
			if set==False:
				usertop_n=top(userID,tr[gen][1])
				g.append((gen,(userID,usertop_n)))
			a,b=calculate_rating(fin,tr[gen][0],usertop_n,userID,movieID)
			ta+=a
			tb+=b
	if tb==0:
		mean=ratmat.mean(axis=1)
		mmean=ratmat.mean(axis=0)
		ome=mean.mean()
		global totalcount
		totalcount+=1
		return mmean[movieID]+(mean[userID]-ome)
	return ta/tb
    
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
		fin,tr=getmatrix(train)
#		print(train)
#		print(train_fr)
#		print(corr)
		
		mae_sum=0
		count=0
		
		for val in list(test.index.values):
#			print("For user ID: "+str(test.loc[val,'userId'])+" Movie ID: "+str(test.loc[val,'movieId'])+" Actual Rating: "+str(test.loc[val,'rating']))
			re=evaluate(fin,tr,int(test.loc[val,'userId']),int(test.loc[val,'movieId']))
			if re>5:
				re=5
#			print("For user ID: "+str(test.loc[val,'userId'])+" Movie ID: "+str(test.loc[val,'movieId'])+" Predicted Rating: "+str(re))
			if re!=-1:
				mae_sum+=abs(test.loc[val,'rating'] - re)
				count+=1
		print("After one iteration without changing Top_N Mean absolute Error :"+str(mae_sum/count))
		overall+=mae_sum
		ocount+=count
	print("Overall without changing Top_N Mean absolute Error :"+str(overall/ocount))
#tr=getmatrix(Ratings)
#print(tr)
#x=evaluate(tr,1,47)
#print(x)
MAE()
#print(totalcount)
