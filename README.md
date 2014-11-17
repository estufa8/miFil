miFil(alpha)
=====

This plugin is an alternative Side Bar for Sublime Text 2 (ST2). It shows configurable colors and a sort of 'icon' for each file extension you set up (by default .js, .php, .css and .html).  

![alt tag](https://raw.github.com/estufa8/miFil/master/demo.png)

To install it copy all the plugin files to a 'miFil' folder in the ST2's Packages folder (in windows: "%APPDATA%\Sublime Text 2\Packages").  

To see it in action, create a file with <b>.fil</b> extension inside your project's folder and open it in ST2.  
This plugin rely on 'view activated' event, so if at first you see the .fil file blank, give focus to another view and come back to it, this will refresh the tree (have to improve this).  

You can double click files and folders to open/fold-unfold them.  

The plugin uses the 'file_exclude_patterns' ST2 user setting to filter the listing.  

Yo can configure new extensions by duplicating an existing one in the file <b>miFil.tmLanguage</b>.
For example, duplicate this <dict> node:  
```
		<dict>
			<key>match</key>
			<string>^.+?\.html$</string>
			<key>name</key>
			<string>html</string>
		</dict>
```
and replace both 'html' apparitions with your new extension  
```
		<dict>
			<key>match</key>
			<string>^.+?\.myext$</string>
			<key>name</key>
			<string>myext></string>
		</dict>
```
To set up its color, edit the file <b>miFil.tmTheme</b>. Duplicate an existing <dict> node, change the <b>name</b> and <b>scope</b> fields to match the new extension and edit the <b>foreground</b> color to your needs.  

For example, duplicate this dict:  
```
		<dict>
			<key>name</key>
			<string>html</string>
			<key>scope</key>
			<string>html</string>
			<key>settings</key>
			<dict>
				<key>foreground</key>
				<string>#E68484</string>
			</dict>
		</dict>
```
replace 'html' by the new extension and change the 'foreground' color as you like:  
```
		<dict>
			<key>name</key>
			<string>myext</string>
			<key>scope</key>
			<string>myext</string>
			<key>settings</key>
			<dict>
				<key>foreground</key>
				<string>#5CB4F7</string>
			</dict>
		</dict>
```

This is a first-stage version and tested only by me (Windows os and ST2 only)  

This is my first ST2 plugin, as well as my first plugin ever made, also my FIRST Python code ever written, and my first repo in Github.   

Sorry for the inconveniences.  


Surely there are some bugs. Im sorry.  

On every 'view.on_activated' event, the .fil file is rewritten dinamically with the folder structure, then saved.
It's saved because the last line contains the path to all the folded directories. This info will be used to automatically fold them all the next time the .fil file is opened.  
<b>COOL feature:</b> You can have as much .fil files as you need in your project hierarchy. Each one will show the tree begining from his own path downwards.    

Feel free to post bugs and feature requests. Or fork this repo if you want. I'll be glad.    

Regards.  

ps: Sublime Text 2 is absolutely awesome, but I really missed icons and colors in the project explorer. Being so easy to create a new syntax color, I tried to solve that with this plugin.


