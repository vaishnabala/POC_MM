import streamlit as st
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from googleapiclient.discovery import build # type: ignore
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set up your API key
API_KEY = api_key = open('APIfile_path.txt', 'r').read().strip()  # file path for API key.txt

# Create a YouTube API client
youtube = build('youtube', 'v3', developerKey=API_KEY)

# Function to search for videos using a keyword (Agent 1)
def search_youtube(query, max_results=50):
    request = youtube.search().list(
        part='snippet',
        q=query,
        type='video',
        maxResults=max_results
    )
    response = request.execute()
    return response['items']

# Function to calculate word frequency in a given text (case-insensitive) (Agent 2)
def word_frequency(text, word):
    word = word.lower()  # Make it case-insensitive
    text = text.lower()
    words = re.findall(r'\b' + re.escape(word) + r'\b', text)
    return len(words)

# Function to process a batch of videos (Agent 2)
def process_video_data(videos, word):
    total_frequency = 0
    for video in videos:
        title = video['snippet']['title']
        description = video['snippet']['description']
        total_frequency += word_frequency(title, word)
        total_frequency += word_frequency(description, word)
    return total_frequency

# Function to aggregate the results (Agent 3)
def aggregate_results(videos, word, max_results=10, batch_size=10):
    # Split the videos into smaller batches for parallel processing
    batches = [videos[i:i + batch_size] for i in range(0, len(videos), batch_size)]
    
    # Use ThreadPoolExecutor to process batches concurrently
    with ThreadPoolExecutor() as executor:
        futures = []
        for batch in batches:
            futures.append(executor.submit(process_video_data, batch, word))
        
        total_frequency = 0
        for future in as_completed(futures):
            total_frequency += future.result()
    
    return total_frequency

# Streamlit UI
st.title("YouTube Word Frequency Checker with Multi-Agent Architecture")
st.write("Enter a word, and the app will search YouTube for videos and calculate how frequently that word appears in video titles and descriptions.")

# User input
word = st.text_input("Enter the word to search for:")

# Submit button
if st.button("Search and Calculate"):
    if word:
        with st.spinner('Searching for videos and calculating frequencies...'):
            # Step 1: Search for videos (Agent 1)
            videos = search_youtube(word)
            
            # Step 2: Aggregate results (Agent 3)
            frequency = aggregate_results(videos, word)
            
            # Display the results
            st.write(f"The word '{word}' appears {frequency} times across {len(videos)} videos.")
            
            # Display details of videos found (UI Agent)
            st.write("### Videos Found:")
            for i, video in enumerate(videos):
                st.subheader(f"Video {i+1}: {video['snippet']['title']}")
                st.write(f"Description: {video['snippet']['description']}")
                st.video(f"https://www.youtube.com/watch?v={video['id']['videoId']}")
    else:
        st.error("Please enter a word to search for.")
