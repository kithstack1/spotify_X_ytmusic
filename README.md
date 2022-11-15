# spotify_X_ytmusic
 - .transfer my songs from youtube music to spotify and from spotify to youtube music.
   * SAMPLE COMMAND: ytmusic -u url -cf credential.json -a transfer --origin youtube --destination spotify --targetplaylist_name new_play
 - .upload my local playlists to spotify and youtube music as well
   * SAMPLE COMMAND: ytmusic --action upload --origin directory_name --destination spotify youtube --targetplaylist_name
 - .download albums, tracks and playlists from both spotifydl and ytmusic,
   # from youtube 
   * SAMPLE DOWNLOAD COMMAND: ytmusic --action download --url resource_url --source youtube  --outputdir . 
 - .download not only mp3 files but also videos of the songs 
   # from spotify
   * SAMPLE DOWNLOAD COMMAND: ytmusic --action download --pref_fileformat video --url url --source spotify --outputdir . 
 - .add metadata to all files i download to my local storage.
 - .download any other youtube media by passing on it's url to the program ,yes ik ytdl offers this but
   SAMPLE DOWNLOAD COMMAND: ytmusic --action download --source youtube --content_type other
 - .search for a song and download it.
   SMAPLE COMMAND: ytmusic --query  search_term --action download --outputdir . --pref_fileformat video 
 want to have all this functionality in one place. 
