'''
Implements image alpha-channel proxy-mapper for tkinter events binding
'''
from PIL.ImageTk import PhotoImage
from functools import wraps
import tkinter as tk


class ImgAlphaProxy:
    '''
    Class should be used ax mix-in during subclassing of tkinter widgets
    Generally, image should be an instance of PIL.Image.Image or provide
    getbands and getdata methods and width attr of above class.
    '''
    alphathreshold = 0
    ownfields = {'cursor', 'image', 'alphathreshold'}

    def __init__(self, *args, **kwargs):
        own = {k: kwargs.pop(k) for k in kwargs.copy()
               if k in self.__class__.ownfields}
        super().__init__(*args, **kwargs)
        self.configure(**own)

    def bind(self, sequence=None, func=None, add=None, proxyfy=True):
        '''
        A wrapper over tkinter bind method
        '''
        assert func is not None or proxyfy, 'Could not proxify, func unset'
        if proxyfy:
            func = self._proxyfy(func)
        return super().bind(sequence=sequence,
                            func=func,
                            add=add)

    def configure(self, *args, **kwargs):
        '''
        A wrapper over tkinter configure method
        '''
        self._attach_image(kwargs)  # changes in-place
        self._set_cursor(kwargs)
        return super().configure(*args, **kwargs)

    config = configure  # alias

    def __setitem__(self, key, value):
        # A bit of magic to route through configure
        kwargs = {key: value}
        return self.configure(**kwargs)

    def _attach_image(self, kwargs, saveininst=True):
        if 'image' in kwargs:
            image = kwargs['image']
            # provided via kwargs or instance or class default
            threshold = kwargs.get('alphathreshold', self.alphathreshold)
            alphaindex = image.getbands().index('A')
            self.alphamask = [val > threshold for val
                              in image.getdata(band=alphaindex)]
            self.__imagewidth = image.width  # need it because list is flat
            image = PhotoImage(image)  # convert for tkinter usage
            if saveininst:
                self.image = image    # save in instance
            kwargs['image'] = image   # change kwargs in-place

    def isinimgzone(self, event):
        '''
        Test event object, whether occured inside image or not
        '''
        x, y = event.x, event.y
        try:
            return self.alphamask[y*self.__imagewidth + x]
        except IndexError:
            return False

    def _proxyfy(self, callback):
        '''
        Wrap event callback so that it fires only in non-alpha zone
        '''
        @wraps(callback)
        def wrapper(event, *args, **kwargs):
            if self.isinimgzone(event):
                # dispatch only if event occurs in non-alpha image zone
                return callback(event, *args, **kwargs)
        return wrapper

    def _set_cursor(self, kwargs):
        cursor = kwargs.pop('cursor', ())
        if cursor:
            parent = super()  # save dispatcher for use in inner function
            active, normal = cursor
            imgzone_cache = False

            def move_handler(event):
                nonlocal imgzone_cache
                isinside = self.isinimgzone(event)  # get cursor position
                if isinside != imgzone_cache:  # transiton
                    parent.configure(cursor=active if isinside else normal)
                    imgzone_cache = isinside
            if not hasattr(self, '__cursor_handler'):
                dispatcher = lambda event: self.__cursor_handler(event)
                self.bind('<Motion>', dispatcher, proxyfy=False)  # dispatch
            self.__cursor_handler = move_handler


class ImgLabelButton(ImgAlphaProxy, tk.Label):
    pass


if __name__ == '__main__':  # Some tests
    import PIL.Image
    root = tk.Tk()
    img = PIL.Image.open('monkey.png')
    l = ImgLabelButton(root, image=img)
    l.pack()
    l.bind('<Button-1>', lambda ev: print('Got press:', ev.x, ev.y))
    l.configure(cursor=('hand2', 'arrow'))
    l.cursor_handler = lambda ev: print('Got move', ev.x, ev.y)
    root.mainloop()
