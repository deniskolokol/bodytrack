# BodyTrack
Simple body tracking and sending the positions of joints via OSC protocol.

Created with MediaPipe.

## Scripts

### Annotating static image

`tracker_img.py` - body tracker for static images. Use path to image(s) as command line options:

    > python tracker_img.py path/to/example1.jpg path/to/example2.jpg

Annnoted image will be placed to the same directory with the filename `path/to/example<N>_annotated.jpg`

### Tracking body with a camera

`tracker.py` - body tracker for camera. Run it:

    > python tracker.py --input <CAMERA_ID> --ipaddress <IP_ADDRESS> --port <PORT>

Dance in front of the camera ;) The coordinates of hands will be sent via OSC.

### OSC server for testing and debugging

`oscsrv.py` - simply listens to several addresses, and prints some information about received packets.

    > python oscsrv.py

Observe the standard output.