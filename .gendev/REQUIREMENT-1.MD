# Presumptions

- A docker container with cosyvoice2 0.5B is running, and port 50000 is serving fastapi

# Requirements

The purpose of this step is to make sure the basic voice cloning functions are working.

## Breakdown

A simple web page with:
- A dropdown list to select reference audio
- A text box showing the Transcript of the reference audio
- A text box for the user to input the texts for voice generation
- An audio playback widget

Requirements for audio control:
- Audio should be streamed to the frontend, meaning audio is played immediately without waiting for the completion of audio generation
- User is able to pause and rewind the audio
- User is able to replay the audio

General layout:
- The web page should have 2 sections, the first section is the reference audio selection and the second section is user text input and audio control

