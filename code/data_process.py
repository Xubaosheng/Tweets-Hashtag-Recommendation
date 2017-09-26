import nltk
import re
from nltk.stem.porter import PorterStemmer
from collections import Counter
from nltk.corpus import words
import json
import operator
import string
import random
import time

def dataProcessing(path):
    start_time = time.time()
    f = open(path)
    data = f.read().split('\n')

    print len(data)
    punctuation = string.punctuation
    punctuation = punctuation.replace('#','')
    punctuation = punctuation.replace('@','')
    stopwords = nltk.corpus.stopwords.words('english') + ['u','im','rt','ummm','b','dont', 'arent','ya','yall','isnt'
                                                          ,'cant','couldnt','wouldnt','wont', 'yr','aint','gonna','ur',
                                                          'didnt','r','wasnt','werent','might','maybe','doesnt','would','shes'
                                                          ,'hes','youre', 'omg','wow', 'damn']
    preposition = ['in', 'at', 'by', 'from', 'on', 'for', 'with', 'about', 'into', 'through', 'between', 'under',
                   'against', 'during', 'without', 'upon', 'toward', 'among', 'within', 'along', 'across', 'behind',
                   'near', 'beyond', 'using', 'throughout', 'despite', 'to', 'beside', 'plus', 'towards', 'concerning',
                   'onto', 'beneath', 'via']
    stopwords += preposition


    f7 = open('test_sample.txt', 'w')
    tweet_num_with_hashtag = tweetsNumWithHashtag(data)
    randomNum = random.sample(range(0, tweet_num_with_hashtag),200)
    print tweet_num_with_hashtag
    print time.time() - start_time

    stemmer = PorterStemmer()
    hashtagTweets = {}
    wordHashtags = {}
    tweetNumWithHashtag = 0
    V = 0
    corpus = []
    f6 = open('tweetsWithHashtag.txt', 'w')
    hashtagWithWholeTweets = {}
    num = 0
    for i in range (0,len(data)):
        # print i
        d = list(data[i].split('\t'))
        if len(d) > 3:
            tweet = re.sub(r'(https?://[^\s]+)', '', d[2], flags=re.MULTILINE)
            tweet = tweet.replace('#', ' #')
            tweet = " ".join(tweet.split())

            if '#' in tweet:
                num += 1
                # print tweetNumWithHashtag
                tweet = tweet.lower()
                tweet = tweet.translate(string.maketrans("",""),punctuation)
                tweetNumWithHashtag += 1
                complier1 = re.compile('#[\w]+')
                hashtag = re.findall(complier1,tweet)
                # print tweet
                hashtag = list(set(hashtag))
                tweet = re.sub(r'(www\.[^\s]+)', '',tweet, flags=re.MULTILINE)
                # new_tweet = re.sub('#[\w]+', '',tweet)
                # print tweet
                if num not in randomNum:
                    f6.write(str(tweet) + '\n')
                    for h in hashtag:
                        # print h
                        if h in tweet:
                            id = tweet.index(h)
                            if id + len(h) < len(tweet) -1:
                                if tweet[id+len(h) +1] != '#':
                                    tweet = tweet.replace(h,h[1:])
                                else:
                                    tweet = tweet.replace(h,'')
                            else:
                                tweet = tweet.replace(h,'')
                    new_tweet = re.sub('@[\w]+', '',tweet)
                    new_tweet = re.sub('[\d]+', '',new_tweet)
                    re.sub(r'[^\x00-\x7F]+','', new_tweet)
                    new_tweet = re.findall('[\w]+',new_tweet)
                    new_tweet = [stemmer.stem(word) for word in new_tweet if word not in stopwords]
                    if len(new_tweet) !=0:
                        V += len(new_tweet)
                        corpus += new_tweet
                        for h in hashtag:
                            if h not in hashtagTweets:
                                hashtagTweets[h] = new_tweet
                                hashtagWithWholeTweets[h] = [tweet]
                            else:
                                hashtagTweets[h] += new_tweet
                                hashtagWithWholeTweets[h] += [tweet]
                        for word in new_tweet:
                            if word not in wordHashtags:
                                wordHashtags[word] = hashtag
                            else:
                                wordHashtags[word] += hashtag
                else:
                    f7.write(str(tweet) + '\n')

    f2 = open('hashtagTweets.txt','w')
    f3 = open('wordHashtags.txt','w')
    for h in hashtagTweets:
        hashtagTweets[h] = Counter(hashtagTweets[h])
        f2.write(str(h) +': ' + str(hashtagTweets[h])+'\n')
    for word in wordHashtags:
        wordHashtags[word] = Counter(wordHashtags[word])
        f3.write(str(word) +': ' + str(wordHashtags[word])+'\n')
    with open('hashtagTweets.json','w') as j1:
        json.dump(hashtagTweets,j1)

    with open('wordHashtags.json','w') as j2:
        json.dump(wordHashtags,j2)

    f4 = open('corpus.txt', 'w')
    f4.write(str(corpus))

    f5 = open('hashtagWithWholeTweets.txt','w')
    for hashtag in hashtagWithWholeTweets:
        f5.write(str(hashtag) + ': ' + str(len(hashtagWithWholeTweets[hashtag]))
                 + ' ' + str(hashtagWithWholeTweets[hashtag]) + '\n\n')


def tweetsNumWithHashtag(data):
    num = 0
    for i in range (0,len(data)):
        d = list(data[i].split('\t'))
        if len(d) > 3:
            tweet = re.sub(r'(https?://[^\s]+)', '', d[2], flags=re.MULTILINE)
            tweet = tweet.replace('#', ' #')
            tweet = " ".join(tweet.split())
            if '#' in tweet:
                num += 1
    return num

def generateTestData():

    f1 = open('tweetsWithHashtag.txt','r')
    data = f1.read().split('\n')
    print len(data)
    randomNum = random.sample(range(0, len(data)),200)
    f2 = open('test_sample.txt','w')
    for i in range(0, len(randomNum)):
        f2.write(str(data[randomNum[i]]) + '\n')



def main():
    dataProcessing(path)
    #generateTestData()

if __name__ == '__main__':
    main()



