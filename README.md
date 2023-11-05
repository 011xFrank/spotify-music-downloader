# Spotify Music Downloader

This is a personal project i created used for downloading music using the link to the song on spotify.

## Setup

1.Ensure you have python3 or later installed.
2.Install the required packages in the requirements.txt file using the command pip install -r requirements.txt
3.Follow the steps on https://cran.r-project.org/web/packages/spotidy/vignettes/Connecting-with-the-Spotify-API.html in order to obtain your spotify Client ID and Client Secret.
4.Add the Client ID,Client Secret on the lines 39,40 respectively.(Instructions Given Between Quotes)
5.Replace the music folder in line 117 with your respective music folder.
6.Replace the working directory in line 118 with your the directory where you will run the python file.

## Usage

Run the following command :
python3 music.py <url to the spotify link>

## Expected Issues

You are likely to run into a issue that states "youtube-dl Unable to extract uploader id"
To resolve this issue you can follow the steps on this youtube video https://www.youtube.com/watch?v=Ghe058HpmMk