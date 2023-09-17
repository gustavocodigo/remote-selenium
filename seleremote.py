import asyncio
import websockets


class SeleRemote:
    def __init__(self, driver):
        self.mouse_script = """{
    let type = arguments[0]
    let x = arguments[1]
    let y = arguments[2]

  var event = new MouseEvent(type, {
    bubbles: true,
    cancelable: true,
    view: window,
    clientX: x,
    clientY: y
  });

  var element = document.elementFromPoint(x, y);

  if (element) {
  
  setTimeout(() => {
        element.dispatchEvent(event);
  },100)
    
    let currentBg = element.style.backgroundColor;
    if ( currentBg == "greenyellow") return;
    element.style.backgroundColor = "greenyellow";
    setTimeout( function() {
        element.style.backgroundColor = currentBg;
    }, 1000);

    
  } else {
    document.dispatchEvent(event);
    
  }
}
"""
        # Start Selenium WebDriver service
      
        
        # Initialize old_url for tracking changes
        self.old_url = ""
        self.driver = driver

    def is_page_fully_loaded(self):
        return self.driver.execute_script("return document.readyState") == "complete"

    async def handle_command(self, message, websocket):
        try:
            if not self.is_page_fully_loaded():
                print("BUSY")
                return
        
            if message.startswith("get_url:"):
                url = message[8:]
                print("SEND GET", url)
                await websocket.send("loading_url:" + url)
                self.driver.get(url)
                await websocket.send("finish_url:" + url)
            
            elif message.startswith("click"):
                _, xFactor, yFactor = message.split('_')
                xFactor = float(xFactor)
                yFactor = float(yFactor)
                if 0 <= xFactor <= 1 and 0 <= yFactor <= 1:
                    window_width = self.driver.execute_script("return window.innerWidth;")
                    window_height = self.driver.execute_script("return window.innerHeight;")
                    x_coord = int(window_width * xFactor)
                    y_coord = int(window_height * yFactor)

                    # Move the mouse to the desired position
                    print(f"Click Position - X: {x_coord}, Y: {y_coord}")
                    self.driver.execute_script(self.mouse_script, "click", x_coord, y_coord)

                else:
                    print("Coordinates are out of window bounds")
            else:
                print(f"Unrecognized message: {message}")
        except Exception as e:
            print(f"Error processing command: {str(e)}")

    async def stream_video(self, websocket):
        try:
            print("Streaming image")
            while True:
                await asyncio.sleep(0.016 * 2)
                screenshot_base64 = self.driver.get_screenshot_as_base64()
                await websocket.send("data:image/png;base64," + screenshot_base64)
                if self.old_url != self.driver.current_url:
                    await websocket.send("current_url:" + self.driver.current_url)
                    self.old_url = self.driver.current_url
        except Exception as e:
            print(f"Error streaming image: {str(e)}")

    async def main(self, websocket, path):
        async def proxy_messages(websocket, queue):
            async for message in websocket:
                print(message)
                await self.handle_command(message, websocket)

        queue = asyncio.Queue()
        await asyncio.gather(proxy_messages(websocket, queue), self.stream_video(websocket))

    def start_server(self,host ="127.0.1",  port=8765):
        try:
            start_server = websockets.serve(self.main, host, port)
            print("Server listening on: ws://"+host+":"+str(port))
            asyncio.get_event_loop().run_until_complete(start_server)
            asyncio.get_event_loop().run_forever()
        finally:
            if self.driver:
                self.driver.quit()
