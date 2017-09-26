import json
import copy
import math
import re
import string
from nltk.stem.porter import PorterStemmer
import nltk
from collections import Counter


# compute the hashtag frequency and inverse corpus frequency
def hfIcf():
    f1 = open('hashtagTweets.json','r')
    f2 = open('wordHashtags.json','r')
    f3 = open('corpus.txt','r')
    wordHashtags = json.load(f2)
    hashtagTweets = json.load(f1)
    corpus = f3.readline().split(',')
    corpus[0] = corpus[0].replace('[','')
    corpus[len(corpus)-1] = corpus[len(corpus)-1].replace(']','')
    V = len(corpus)

    hashtagFrequency = copy.deepcopy(wordHashtags)
    # f4 = open('../out/hashtagFrequency.txt','w')
    for word in wordHashtags:
        allHashtagNum = sum([wordHashtags[word][h] for h in wordHashtags[word]])
        for hashtag in wordHashtags[word]:
            hashtagFrequency[word][hashtag] = float(wordHashtags[word][hashtag])/allHashtagNum
        # f4.write(str(word) +': ' + str(allHashtagNum)+' '+ str(hashtagFrequency[word]) + '\n')

    inverseCorpusFrequency = {}
    # f5 = open('../out/inverseCorpusFrequency.txt','w')
    for hashtag in hashtagTweets:
        allWordSum = sum(hashtagTweets[hashtag][word] for word in hashtagTweets[hashtag])
        # allWordSum2 = len(hashtagTweets[hashtag])
        inverseLog = math.log(V) - math.log(allWordSum)
        inverseCorpusFrequency[hashtag] = inverseLog
        # f5.write(str(hashtag) + ': '+ str(allWordSum)+' '+ str(inverseLog) + '\n')

    return hashtagFrequency,inverseCorpusFrequency

# sort hashtag according to the value of it
def sortedHashtag(hashtagFrequency, inverseCorpusFrequency):
    sortedWordHashtags = {}
    for word in hashtagFrequency:
        hashtagWithValue = []
        for hashtag in hashtagFrequency[word]:
            value = hashtagFrequency[word][hashtag] * inverseCorpusFrequency[hashtag]
            hashtagWithValue.append((hashtag, value))
        hashtagWithValue = sorted(hashtagWithValue, key= lambda hashtagWithValue: hashtagWithValue[1], reverse = True)
        sortedWordHashtags[word] = hashtagWithValue
    return sortedWordHashtags


# generate the ten hashtags for the tweet
def hashtagRecommend(tweet,hashtagFrequency,inverseCorpusFrequency,stopwords):
    punctuation = string.punctuation
    punctuation = punctuation.replace('#','')
    punctuation = punctuation.replace('@','')
    stemmer = PorterStemmer()
    # tweet = tweet.lower()
    # tweet = re.sub(r'(www\.[^\s]+)', '',tweet, flags=re.MULTILINE)
    # tweet = re.sub('#[\w]+', '',tweet)
    # tweet = re.sub('@[\w]+', '',tweet)
    # tweet = re.sub('[\d]+', '',tweet)
    # re.sub(r'[^\x00-\x7F]+','', tweet)
    # tweet = tweet.translate(string.maketrans("",""),string.punctuation)
    # tweet = re.findall('[\w]+',tweet)
    # tweet = [stemmer.stem(word) for word in tweet if word not in stopwords]
    tweet = tweet.replace('#', ' #')
    tweet = " ".join(tweet.split())
    tweet = tweet.lower()
    tweet = tweet.translate(string.maketrans("",""),punctuation)
    complier1 = re.compile('#[\w]+')
    hashtag = re.findall(complier1,tweet)

    hashtag = list(set(hashtag))
    tweet = re.sub(r'(www\.[^\s]+)', '',tweet, flags=re.MULTILINE)
    for h in hashtag:
        if h in tweet:
            id = tweet.index(h)
            if id + len(h) < len(tweet) -1:
                if tweet[id+len(h) +1] != '#':
                    tweet = tweet.replace(h,h[1:])
                else:
                    tweet = tweet.replace(h,'')
            else:
                tweet = tweet.replace(h,'')
    tweet = re.sub('@[\w]+', '',tweet)
    tweet = re.sub('[\d]+', '',tweet)
    re.sub(r'[^\x00-\x7F]+','', tweet)
    tweet = re.findall('[\w]+',tweet)
    tweet = [stemmer.stem(word) for word in tweet if word not in stopwords]
    tweet = list(set(tweet))

    tweetScore = []
    if len(tweet) > 0:
        # print tweet
        for i in range(0,len(tweet)):
            word = tweet[i]
            score =0
            if word in hashtagFrequency:
                for hashtag in hashtagFrequency[word]:
                    score += hashtagFrequency[word][hashtag] * inverseCorpusFrequency[hashtag]
            tweetScore.append((word,score))

    tweetScore = sorted(tweetScore, key= lambda tweetScore: tweetScore[1], reverse= True)
    return tweetScore


# compute the accuracy of the hashtag prediction
def accuracy(tweets_set, hashtagFrequency,inverseCorpusFrequency,sortedWordHashtags):
    stopwords = nltk.corpus.stopwords.words('english') + ['u','im','rt','ummm','b','dont', 'arent','ya','yall','isnt'
                                                          ,'cant','couldnt','wouldnt','wont', 'yr','aint','gonna','ur',
                                                          'didnt','r','wasnt','werent','might','maybe','doesnt','would','shes'
                                                          ,'hes','youre', 'omg','us', 'wow']

    preposition = ['in', 'at', 'by', 'from', 'on', 'for', 'with', 'about', 'into', 'through', 'between', 'under',
                   'against', 'during', 'without', 'upon', 'toward', 'among', 'within', 'along', 'across', 'behind',
                   'near', 'beyond', 'using', 'throughout', 'despite', 'to', 'beside', 'plus', 'towards', 'concerning',
                   'onto', 'beneath', 'via']
    stopwords += preposition

    correctNum = 0
    totalTweetsNum = 0
    for data in tweets_set:
        tweet = re.sub(r'(https?://[^\s]+)', '', data, flags=re.MULTILINE)
        if '#' in tweet:
            tweet = tweet.lower()
            print tweet
            complier1 = re.compile('#[\w]+')
            hashtags = re.findall(complier1,tweet)
            print hashtags
            rankedWords = \
                hashtagRecommend(tweet,hashtagFrequency,inverseCorpusFrequency,stopwords)
            hashtagRecommended = []
            num = 0
            less = 0
            for i in range(0, len(rankedWords)):
                num_per_word = 0
                if num == 10:
                    break
                hashtagNum = 0
                if i < 4:
                    hashtagNum = 4 -i + less
                else:
                    hashtagNum = 2
                if rankedWords[i][1] !=0:
                    for j in range(0, hashtagNum):
                        if j == len(sortedWordHashtags[rankedWords[i][0]]):
                            break
                        hashtagRecommended.append(sortedWordHashtags[rankedWords[i][0]][j][0])
                        num += 1
                        num_per_word += 1
                    less = hashtagNum - num_per_word

                else:
                    break

# generate different number of hashtags
#############################################################################################################
            # if len(rankedWords) >= 4:
            #     if rankedWords[0][1] !=0:
            #         if len(sortedWordHashtags[rankedWords[0][0]]) >=4:
            #                 hashtagRecommended.append(sortedWordHashtags[rankedWords[0][0]][0][0])
            #                 hashtagRecommended.append(sortedWordHashtags[rankedWords[0][0]][1][0])
            #                 hashtagRecommended.append(sortedWordHashtags[rankedWords[0][0]][2][0])
            #                 hashtagRecommended.append(sortedWordHashtags[rankedWords[0][0]][3][0])
            #                 num += 4
            #         else:
            #              for i in range (0, len(sortedWordHashtags[rankedWords[0][0]])):
            #                 hashtagRecommended.append(sortedWordHashtags[rankedWords[0][0]][i][0])
            #                 num += 1
            #     if rankedWords[1][1] !=0:
            #         if len(sortedWordHashtags[rankedWords[1][0]]) >=3:
            #             hashtagRecommended.append(sortedWordHashtags[rankedWords[1][0]][0][0])
            #             hashtagRecommended.append(sortedWordHashtags[rankedWords[1][0]][1][0])
            #             hashtagRecommended.append(sortedWordHashtags[rankedWords[1][0]][2][0])
            #             num += 3
            #         else:
            #             for i in range (0, len(sortedWordHashtags[rankedWords[1][0]])):
            #                 hashtagRecommended.append(sortedWordHashtags[rankedWords[1][0]][i][0])
            #                 num += 1
            #     if rankedWords[2][1] !=0:
            #         if len(sortedWordHashtags[rankedWords[2][0]]) >=2:
            #             hashtagRecommended.append(sortedWordHashtags[rankedWords[2][0]][0][0])
            #             hashtagRecommended.append(sortedWordHashtags[rankedWords[2][0]][1][0])
            #             num += 2
            #         else:
            #             for i in range (0, len(sortedWordHashtags[rankedWords[2][0]])):
            #                 hashtagRecommended.append(sortedWordHashtags[rankedWords[2][0]][i][0])
            #                 num += 1
            #     if rankedWords[3][1] !=0:
            #         hashtagRecommended.append(sortedWordHashtags[rankedWords[3][0]][0][0])
            #         num +=1
            #     if num < 10:
            #         for i in range(4, len(rankedWords)):
            #             if num == 10:
            #                 break
            #             if rankedWords[i][1] !=0:
            #                 hashtagRecommended.append(sortedWordHashtags[rankedWords[i][0]][0][0])
            #                 num += 1
            #             else:
            #                 break
            #
            # else:
            #     for i in range(0, len(rankedWords)):
            #         j = 0
            #         if rankedWords[i][1] != 0:
            #             while (j <= 4 - i):
            #                 if j == len(sortedWordHashtags[rankedWords[i][0]]):
            #                         break
            #                 if rankedWords[i][1] != 0:
            #                     hashtagRecommended.append(sortedWordHashtags[rankedWords[i][0]][j][0])
            #                     j += 1
            #                 else:
            #                     break
            #         else:
            #             break
#############################################################################################################
            if len(hashtagRecommended) != 0:
                totalTweetsNum += 1
                correct = False
                for h in hashtags:
                    if h in hashtagRecommended:
                        correctNum += 1
                        correct = True
                        break
                print rankedWords
                print correct, Counter(hashtagRecommended)
                print ' '
    print 'correctNum: ', correctNum, 'totalTweetsNum: ', totalTweetsNum
    return float(correctNum)/totalTweetsNum



def main():
    f1 = open('test_sample.txt','r')
    tweets_set = f1.read().split('\n')
    [hashtagFrequency,inverseCorpusFrequency] = hfIcf()
    sortedWordHashtags = sortedHashtag(hashtagFrequency,inverseCorpusFrequency)
    ac = accuracy(tweets_set, hashtagFrequency,inverseCorpusFrequency,sortedWordHashtags)
    print 'accuracy', ac




if __name__ == '__main__':
    main()