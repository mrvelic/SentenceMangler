#!/usr/bin/python
## Small program that uses difflib to mess up sentences
## Multithreading is used to minimize the search space in the dictionary for each difflib operation
## Mirko Velic - 2013

import re, collections, difflib, random, multiprocessing, threading, Queue

def words(text): return re.findall('[a-z]+', text.lower()) 

THREAD_SCALE = 2
WORDS = words(file('words.txt').read())
CPU_COUNT = multiprocessing.cpu_count() * THREAD_SCALE
WORD_SPLIT = len(WORDS) / CPU_COUNT
THREAD_MATCHES = []


def get_words(cpu, word):
	# splice words by thread number
	global THREAD_MATCHES
	start_from = cpu * WORD_SPLIT
	#print "Thread {0} Starting from: {1}".format(cpu, start_from)

	THREAD_MATCHES.put(difflib.get_close_matches(word, WORDS[start_from:WORD_SPLIT], 10))

def similar_word(word):
	global THREAD_MATCHES
	if len(word) > 2:
		threads = []
		matches = []
		THREAD_MATCHES = Queue.Queue()

		# start threads
		for c in range(0, CPU_COUNT):
			t = threading.Thread(target=get_words, args=(c, word))
			t.daemon = True

			threads.append(t)
			t.start()

		# wait for threads to complete
		for t in threads:
			t.join()
	
		# get results
		while not THREAD_MATCHES.empty():
			matches.extend(THREAD_MATCHES.get())

		# remove anything thats the same word
		matches = [m for m in matches if m != word]

		# if there are any matches, return a random word from the set
		if len(matches) > 0:
			match_index = random.randint(0, (len(matches) - 1))
			return matches[match_index]		

	return word		

def main():
	print "Word Count: {0}".format(len(WORDS))

	while True:
		input = raw_input("Input: ")
		if input == "q":
			quit()

		word_list = words(input)

		changed_words = []

		for w in word_list:
			changed_words.append(similar_word(w))

		print " ".join(changed_words)

if __name__ == "__main__":
	main()
