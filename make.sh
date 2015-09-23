sudo rm -rf output/*
pyinstaller  --distpath=output/mainb/dist  --workpath=output/mainb/build ui/main.py
pyinstaller  --distpath=output/getpassb/dist  --workpath=output/getpassb/build passget/getpass.py
pyinstaller  --distpath=output/checkpassb/dist  --workpath=output/checkpassb/build passcheck/checkpass.py
pyinstaller  --distpath=output/viewerb/dist  --workpath=output/viewerb/build viewer/viewer.py
pyinstaller  --distpath=output/ssudob/dist  --workpath=output/ssudob/build sample_client/ssudo.py


cp -rf output/mainb/dist/main/* output/
cp -rf output/getpassb/dist/getpass/* output/
cp -rf output/checkpassb/dist/checkpass/* output/
cp -rf output/viewerb/dist/viewer/* output/
cp -rf output/ssudob/dist/ssudo/* output/


cp passcheck/*.conf output/
cp ui/*.conf output/
cp passget/*.conf output/
cp viewer/*.conf output/


echo -e "[access]\nexe=`pwd`/output/main\nsha1=`sha1sum output/main | awk '{print $1}'`" >> output/passget.conf
echo -e "[access]\nexe=`pwd`/output/main\nsha1=`sha1sum output/main | awk '{print $1}'`" >> output/passcheck.conf
echo -e "[access]\nexe=`pwd`/output/main\nsha1=`sha1sum output/main | awk '{print $1}'`" >> output/viewer.conf



sudo chgrp input output/getpass
sudo chgrp input output/passget.conf
sudo chmod g+s output/getpass


sudo chgrp passchecker output/checkpass
sudo chgrp passchecker output/passcheck.conf
sudo chown root output/passcheck.conf
sudo chmod g+s output/checkpass
sudo chmod 770 output/passcheck.conf


sudo chgrp input output/viewer
sudo chgrp input output/viewer.conf
sudo chmod g+s output/viewer

cd output
./main --initdb