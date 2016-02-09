Just copy the plugin ﬁle to the Hooke directory and edit the plugin section in
your hooke.conf. It looks something like this:

```
<plugins>
     <fit/>
     <procplots/>
     <flatfilts/>
</plugins>
```

Add a tag with your plugin ﬁlename in the same fashion:

```
<plugins>
     <fit/>
     <procplots/>
     <flatfilts/>
     <my-new-fancy-plugin/>
</plugins>
```

> Restart Hooke. At startup you should see that your plugin has been loaded
and by typing ’help’, you’ll ﬁnd ’mycommand’ among the others. The same
syntax holds for drivers.