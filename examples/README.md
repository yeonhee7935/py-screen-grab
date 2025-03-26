# WebRTC Screen Sharing Example

This example demonstrates how to stream screen captures using WebRTC between Python (sender) and a web browser (receiver).

<br/>
<br/>

## 🔧 Prerequisites

- Python 3.7+
- Web browser (Chrome recommended)
- Required Python packages:
  ```bash
  pip install -r requirements.txt
  ```

<br/>
<br/>

## 🚀 Running the Example

### 1. Start the Python Sender

1. Run the Python script:

   ```bash
   python -m examples.index
   ```

2. When prompted, enter the window name you want to capture (e.g., "RViz")

3. The script will generate a WebRTC offer. Copy this offer data (it will be in JSON format).

### 2. Set up the Browser Receiver

1. Open `index.html` in your web browser

   - You can use a simple HTTP server:
     ```bash
     python -m http.server
     ```
   - Then visit `http://localhost:8000/index.html`

2. In the browser:
   - Paste the copied offer data into the "Python Offer" textarea
   - Click the "Set Offer" button
   - The browser will generate an answer - copy this answer

### 3. Complete the Connection

1. Go back to the Python terminal
2. Paste the browser's answer when prompted
3. The connection should establish, and you'll see the screen stream in your browser

<br/>
<br/>

## 📊 Connection Status

- The web page displays the current connection status
- The video stream will appear in the browser once the connection is established
- You can monitor the connection state in both Python logs and browser console

<br/>
<br/>

## 🛑 Stopping the Stream

- Press Ctrl+C in the Python terminal to stop the stream
- The connection will be automatically cleaned up

<br/>
<br/>

## ❗ Troubleshooting

- If the connection fails, ensure both devices are on the same network
- Check browser console for any error messages
- Verify that the window name entered in Python exactly matches the target window
- If the stream is black, verify that the window is visible and not minimized

<br/>
<br/>

## 📝 Notes

- The example uses Google's public STUN server for NAT traversal
- Video is streamed at 30 FPS by default
- The connection uses VP8 video codec
- Screen capture is converted from BGR to RGB format before streaming
