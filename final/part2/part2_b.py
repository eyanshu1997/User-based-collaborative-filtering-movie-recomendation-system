import pandas as pd
import random
import argparse
from operator import itemgetter 
import numpy as np
import random
import itertools
import csv

parser = argparse.ArgumentParser()
parser.add_argument('--input',help='enter the input')
parser.add_argument('--output',help="enter the output location")
args=parser.parse_args()
#print(args)	
if args.input==None or args.output==None:
	print("wrongs args")
	exit()

#movies = pd.read_csv("movies.csv",encoding="Latin1")
Ratings = pd.read_csv("ratings.csv",nrows=50000)
read_rating = pd.read_csv('movies.csv')




um_withnan=pd.pivot_table(Ratings,values='rating',index='userId',columns='movieId')
um_i=((um_withnan*0)+1)
um_c=um_i.fillna(0)
enre=set()
genre=set()
for x in range(9742):
    val=read_rating.iloc[x,2]
    val=val.split("|")
#    print(val)
    [genre.add(y) for y in val]

genre_mov=dict()
id_list=[]
genre_mov[""]=[]

ratmat=pd.pivot_table(pd.read_csv("ratings.csv",nrows=40000),values='rating',index='userId',columns='movieId')
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
	final=pd.pivot_table(Ratings,values='rating',index='userId',columns='movieId')
#	print(final.loc[:,1])
	Ratmat=final
	y=genre_corelation(genre,final)
	fi={}
	for x in y:
		

	#print(final)
		z=y[x].fillna(y[x].mean(axis=0))
	#print(final)
		corr=z.transpose()
		corr_final=corr.corr(method='pearson')
		fi[x]=[y[x],corr_final]
	return final,fi


        
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
            if not (np.isnan(final.loc[res[x][0],movie])):
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
		return mmean[movieID]+(mean[userID]-ome)
	return ta/tb
	
def process(userlist,ratings):
    fin,tr=getmatrix(ratings)
    pr=[]
    ac=[]
#	print(fin)
#	fin.to_csv("a.csv")
    for i in userlist:	
        mov={}
        seen=set()
#		print(fin)
#		print(fin.loc[int(i),:])
        us=fin.loc[int(i),:].notna()
#		print(us)
        for x in fin.columns:
            if us[x]==True:
                seen.add(x)
#		print(us.index)
#		print(len(seen))
		#print(seen)
        for j in fin.columns:
            if j not in seen:
                re=evaluate(fin,tr,int(i),j)
                if re>5:
                    re=5
                mov[j]=re
        res = dict(sorted(mov.items(), key = itemgetter(1), reverse = True)[:5])
        print(res)
        pr.append(res)
        use=fin.loc[int(i),:]
        print(use.nlargest())
        ac.append(use.nlargest().to_dict())
    return pr,ac
	  	
	   	
	  
file1 = open(args.input, 'r') 
#Lines = file1.readlines()
#process(Lines,Ratings)
userlist=[]
fields = ['Test_user', 'P_Movies','P_Ratings','Past_Movies','Past_Ratings']
u_list=file1.readlines()
print(u_list)
pr,ac=process(u_list,Ratings)
print("pr : \n",pr)
print("ac : \n",ac)
mydict =[]
app={'Test_user':0,'P_Movies':0,'P_Ratings':0,'Past_Movies':0,'Past_Ratings':0}
i=0

for i in range(len(u_list)):
	for j,k in zip(pr[i],ac[i]):
		app={'Test_user':u_list[i],'P_Movies':j,'P_Ratings':pr[i][j],'Past_Movies':k,'Past_Ratings':ac[i][k]}
		mydict.append(app)
	    
#print(mydict)
filename = "output2.csv"
  
# writing to csv file 
with open(filename, 'w') as csvfile: 
    # creating a csv dict writer object 
    writer = csv.DictWriter(csvfile, fieldnames = fields) 
      
    # writing headers (field names) 
    writer.writeheader() 
      
    # writing data rows 
    writer.writerows(mydict) 
# process(Lines,Ratings)


