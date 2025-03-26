import asyncio
import logging
import json
from py_screen_grab.screen_grabber import ScreenGrabber
from .webrtc_stream import WebRTCStream

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    print("\n=== Please enter the window name and press Enter(ex: RViz) ===\n")
    window_name = input().strip()

    grabber = ScreenGrabber().set_window(window_name=window_name)
    
    try:
        # Start streaming
        frame_subject = await grabber.start_streaming()
        webrtc = WebRTCStream(frame_subject)
        
        # Generate and wait for offer
        logger.info("Generating offer...")
        offer_data = await webrtc.start()
        
        # Pretty print the offer for easy copying
        print("\n=== Local SDP Offer (copy this) ===\n")
        print(json.dumps(json.loads(offer_data), indent=2))
        
        # Wait for answer
        print("\n=== Paste Remote SDP Answer (including ICE candidates) and press Enter ===\n")
        answer_data = input().strip()
        
        if not answer_data:
            logger.error("No answer provided")
            return

        try:
            logger.info("Processing answer...")
            await webrtc.handle_answer(answer_data)
            print("\nConnection established! Streaming... (Press Ctrl+C to stop)")
            
            # Keep connection alive
            while True:
                await asyncio.sleep(1)
                if not webrtc.pc or webrtc.pc.connectionState == "closed":
                    logger.error("Connection closed unexpectedly")
                    break
                
        except ConnectionError as e:
            logger.error(f"Connection failed: {e}")
            
    except KeyboardInterrupt:
        print("\nStopping...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        if 'webrtc' in locals():
            await webrtc.stop()
        await grabber.stop_streaming()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram terminated by user") 