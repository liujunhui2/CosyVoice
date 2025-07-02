# Requirements for the second step

In this step, we will add voice recording for this demo

# Requirements
- Add a reminder to the user: "为达到最佳效果，请在安静的环境录制音频，并按照提示调整语音"
- Each recording will have a user id entered by the user
- Each recording will have a tag, from a predefined list, [Normal, Strong, Soft]
- Each tag will correspond to a predefined text and a hint:
  -- Tag: Normal, Text: "今天我们要聊一个很多人都困惑的话题——如何在忙碌的生活中找到真正属于自己的时间。我最近采访了三位在不同行业工作的朋友，他们都有一个共同点：在极度忙碌的工作中，依然保持着高质量的个人生活。", Hint: "正常语速的日常语音"
  -- Tag: Strong, Text: "白日依山尽，黄河入海流。欲穷千里目，更上一层楼", Hint: "朗诵或者强调，慢语速"
  -- Tag: Soft, Text: "最近你经历了很多，压力很大，但这一切都会过去的，给自己一点时间和空间。有时候，我们需要放慢脚步，才能更清楚地看见前方的路。如果累了，就休息一下吧，没人会责怪你。这杯茶还是热的，慢慢喝，让心也跟着平静下来。", Hint: "轻柔的声音"
- Text is prefilled, but user can also edit it
- After user voice is recorded, the audio file is sent to backend
- First the audio file is transcribed calling Amazon Transcribe, and the trancribed text is displayed for user reference. There is an option for the user to fill the text input with transcribed text
- Then the user is able to submit the final audio file and corresponding text

# UI suggestion
There will be a number of modifications of the previous step.
1. User can switch between recording mode and reference mode.
1.1 The recroding mode is only for uploading recording, tags, and corresponding text
1.2 The saved recording file and text can be named with <userid>_<tag>.wav and <userid>_<tag>.txt
1.3 The uploaded recording and text is available for later voice generation as a selectable reference
1.4 In recording mode, voice generation block is hidden and visable again when user switch back to the voice generation mode
2. User can only generate voice in reference mode. In reference mode, user can select preset audio, or multiple audios under a single user id
2.1 For this version, only one recorded audio can be selected
3. The backend will use the selected audio and reference text for voice generation

# Updated Implementation Details (Latest Changes)
- **Commit Function**: Replace "Upload Recording" with "Commit Recording" button
- **Post-Commit Behavior**: Show success message, keep user ID, clear other inputs (tag, text, recorded audio)
- **File Storage**: Recordings saved to `asset/recorded/` folder instead of webapp assets
- **Transcription**: Keep AWS Transcribe functionality for user review and text editing
- **File Upload Removal**: Remove file upload button functionality (only microphone recording)
- **Reference Mode**: Committed recordings available for selection in voice generation
- **API Endpoint**: New `/api/commit-recording` endpoint for saving to asset/recorded folder
- **Backward Compatibility**: System checks both old and new storage locations for existing recordings
