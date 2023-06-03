@Echo Off

python del_touched.py

Echo Simulating normal network activity
Echo.
CD users

for /l %%N in (1 1 3) DO (
	Echo Starting round %%N
	FOR /D %%G in ("*") DO (
		Echo %%G:
		CD %%~nxG
		java -jar -Dcom.sun.jndi.ldap.object.trustURLCodebase=true DofenMail.jar
		CD ..
	)
	Echo.
	Echo.
)

if exist CEO/HelloWorld (
	color a
	start /wait https://youtu.be/FJeBHiDOTPE
	cls
	Echo Y0u w0n 4nd h4ck3d 4ll the th1ngs
	Rem start /wait https://youtu.be/2xZZJjRWlas?t=59
	rm CEO/HelloWorld
	Echo You are indeed a pro hacker cracker
	Echo Removed the file so you can try again
	Echo.
	Echo If you wish to retry the test just re-run the program
	@pause
	color
	cls
) else (
	Echo Couldn't find file HelloWorld in the CEO directory
	Echo Try again
	@pause
)

CD ..

python del_touched.py