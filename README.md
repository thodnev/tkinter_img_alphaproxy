# tkinter_img_alphaproxy
Implements button widget, which handles tkinter events on images with alpha-channel properly

There's a big problem with how tkinter handles events on images with alpha-channel, which is the main point why beautiful rounded buttons are really rare used in tkinter apps.
If you create a Button or Label widget with image, there's no uncomplicated way to handle events (like key presses) only above the non-transparent part of a image.
You could deal with it, if you capture tkinter events and check, whether they occur inside or outside the visible part of the image. But doing so by hand is a bit evil.


This implementation solves problem (I hope), and brings useful widget.
Requirements: Python 3 (tested under 3.5), PIL or Pillow
The main widget is ImgLabelButton, which inherits from Label and has next differencies:
- `image` parameter should be an instance of PIL.Image.Image or provide `getbands` and `getdata` methods and `width` attr of above class.
- `threshold` parameter specifies cut-off value of image alpha-channel. Pixels having alpha above `threshold` are meant to be active, others not.
- `cursor` parameter now accepts a 2-tuple of `(cursor_active, cursor_normal)`, which allows cursor to change when it's over visible zone of the image
- `bind` method has extra `proxyfy` parameter, when set to `True`, proxyfies passed-in callback function to act only in non-alpha (under threshold) zone of image
- `isinimgzone` method is intended to be used for event testing, whether occured inside visible or transparent zone of the image
- `command` parameter not handled *(this is by design, in that particular case it's better to bind a <Button-1> mouse click event etc than to assume)

Here's how it works, cursor changes while over non-transparent part of the image:
![demo](https://cloud.githubusercontent.com/assets/16870636/17231023/2fa14980-5528-11e6-9510-5c726e5426fc.png)
*For more try it on your own

TODO:
Code needs a little cleaning and refactoring.
Improve for common usage scenarios.
