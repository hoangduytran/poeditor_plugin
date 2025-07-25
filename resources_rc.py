# Resource object code (Python 3)
# Created by: object code
# Created by: The Resource Compiler for Qt version 6.9.1
# WARNING! All changes made in this file will be lost!

from PySide6 import QtCore

qt_resource_data = b"\
\x00\x00\x08t\
/\
* Activity Bar S\
tyles - IMMUTABL\
E */\x0a/* This fil\
e should NEVER b\
e changed to mai\
ntain consistent\
 activity bar ap\
pearance */\x0a/* A\
ctivity bar alwa\
ys uses dark the\
me regardless of\
 selected theme \
*/\x0a\x0a/* === ACTIV\
ITY BAR CONTAINE\
R === */\x0a/* Usin\
g !important to \
prevent theme CS\
S from overridin\
g */\x0aQWidget[obj\
ectName=\x22activit\
y_bar\x22] {\x0a    ba\
ckground-color: \
#2c2c2c !importa\
nt;\x0a    border-r\
ight: 1px solid \
#3e3e42 !importa\
nt;\x0a    min-widt\
h: 48px !importa\
nt;\x0a    max-widt\
h: 48px !importa\
nt;\x0a    color: #\
cccccc !importan\
t;\x0a}\x0a\x0a/* Ensure \
any child widget\
s in activity ba\
r also maintain \
dark theme */\x0aQW\
idget[objectName\
=\x22activity_bar\x22]\
 QWidget {\x0a    b\
ackground-color:\
 #2c2c2c !import\
ant;\x0a    color: \
#cccccc !importa\
nt;\x0a}\x0a\x0a/* === AC\
TIVITY BUTTONS =\
== */\x0aQPushButto\
n[objectName^=\x22a\
ctivity_button\x22]\
 {\x0a    backgroun\
d-color: transpa\
rent !important;\
\x0a    border: non\
e !important;\x0a  \
  border-left: 2\
px solid transpa\
rent !important;\
\x0a    color: #858\
585 !important;\x0a\
    font-size: 1\
6px;\x0a    padding\
: 0px;\x0a    margi\
n: 0px;\x0a    min-\
height: 48px;\x0a  \
  max-height: 48\
px;\x0a    min-widt\
h: 48px;\x0a    max\
-width: 48px;\x0a  \
  text-align: ce\
nter;\x0a}\x0a\x0aQPushBu\
tton[objectName^\
=\x22activity_butto\
n\x22]:hover {\x0a    \
background-color\
: #37373d !impor\
tant;\x0a    border\
-left: 2px solid\
 transparent !im\
portant;\x0a    col\
or: #cccccc !imp\
ortant;\x0a}\x0a\x0aQPush\
Button[objectNam\
e^=\x22activity_but\
ton\x22]:pressed {\x0a\
    background-c\
olor: #37373d !i\
mportant;\x0a    co\
lor: #ffffff !im\
portant;\x0a}\x0a\x0a/* A\
ctive state styl\
ing */\x0aQPushButt\
on[objectName^=\x22\
activity_button\x22\
][active=\x22true\x22]\
 {\x0a    color: #f\
fffff !important\
;\x0a    background\
-color: #37373d \
!important;\x0a    \
border-left: 2px\
 solid #0078d4 !\
important;\x0a}\x0a\x0aQP\
ushButton[object\
Name^=\x22activity_\
button\x22][active=\
\x22true\x22]:hover {\x0a\
    background-c\
olor: #414145 !i\
mportant;\x0a    bo\
rder-left: 2px s\
olid #0078d4 !im\
portant;\x0a    col\
or: #ffffff !imp\
ortant;\x0a}\x0a\x0a/* ==\
= ACTIVITY BAR L\
AYOUT === */\x0aQVB\
oxLayout {\x0a    m\
argin: 0px;\x0a    \
padding: 0px;\x0a}\x0a\
\x0a/* === ACTIVITY\
 BAR ICONS === *\
/\x0a/* Icon colors\
 are handled pro\
grammatically by\
 ActivityButton:\
 */\x0a/* - Gray (#\
858585) icons fo\
r inactive state\
 */\x0a/* - White (\
#ffffff) icons f\
or active and ho\
ver states */\x0a/*\
 CSS handles bac\
kground colors a\
nd borders only \
*/\x0a\
\x00\x00\x01\xd3\
<\
?xml version=\x221.\
0\x22 encoding=\x22UTF\
-8\x22?>\x0a<svg width\
=\x2216\x22 height=\x2216\
\x22 viewBox=\x220 0 1\
6 16\x22 fill=\x22none\
\x22 xmlns=\x22http://\
www.w3.org/2000/\
svg\x22>\x0a  <path d=\
\x22M8 0C5.8 0 4 1.\
8 4 4C4 6.2 5.8 \
8 8 8C10.2 8 12 \
6.2 12 4C12 1.8 \
10.2 0 8 0ZM8 6C\
6.9 6 6 5.1 6 4C\
6 2.9 6.9 2 8 2C\
9.1 2 10 2.9 10 \
4C10 5.1 9.1 6 8\
 6ZM14 12C14 10.\
3 11.3 9 8 9C4.7\
 9 2 10.3 2 12V1\
4C2 14.6 2.4 15 \
3 15H13C13.6 15 \
14 14.6 14 14V12\
ZM12 13H4V12C4 1\
1.2 6.7 11 8 11C\
9.3 11 12 11.2 1\
2 12V13Z\x22 fill=\x22\
#ffffff\x22/>\x0a</svg\
>\x0a\
\x00\x00\x01\xdc\
<\
?xml version=\x221.\
0\x22 encoding=\x22UTF\
-8\x22?>\x0a<svg width\
=\x2216\x22 height=\x2216\
\x22 viewBox=\x220 0 1\
6 16\x22 fill=\x22none\
\x22 xmlns=\x22http://\
www.w3.org/2000/\
svg\x22>\x0a  <path d=\
\x22M8 0.5C7.17 0.5\
 6.5 1.17 6.5 2V\
6.5H2C1.17 6.5 0\
.5 7.17 0.5 8S1.\
17 9.5 2 9.5H6.5\
V14C6.5 14.83 7.\
17 15.5 8 15.5S9\
.5 14.83 9.5 14V\
9.5H14C14.83 9.5\
 15.5 8.83 15.5 \
8S14.83 6.5 14 6\
.5H9.5V2C9.5 1.1\
7 8.83 0.5 8 0.5\
Z\x22 fill=\x22#858585\
\x22/>\x0a  <circle cx\
=\x2212\x22 cy=\x224\x22 r=\x22\
2\x22 fill=\x22#858585\
\x22/>\x0a  <circle cx\
=\x224\x22 cy=\x2212\x22 r=\x22\
2\x22 fill=\x22#858585\
\x22/>\x0a</svg>\x0a\
\x00\x00\x01\x9e\
<\
?xml version=\x221.\
0\x22 encoding=\x22UTF\
-8\x22?>\x0a<svg width\
=\x2216\x22 height=\x2216\
\x22 viewBox=\x220 0 1\
6 16\x22 fill=\x22none\
\x22 xmlns=\x22http://\
www.w3.org/2000/\
svg\x22>\x0a  <path d=\
\x22M15.7 13.3L11 8\
.6C11.6 7.7 12 6\
.6 12 5.5C12 2.5\
 9.5 0 6.5 0S1 2\
.5 1 5.5S3.5 11 \
6.5 11C7.6 11 8.\
7 10.6 9.6 10L14\
.3 14.7C14.7 15.\
1 15.3 15.1 15.7\
 14.7C15.9 14.3 \
15.9 13.7 15.7 1\
3.3ZM6.5 9C4.6 9\
 3 7.4 3 5.5S4.6\
 2 6.5 2S10 3.6 \
10 5.5S8.4 9 6.5\
 9Z\x22 fill=\x22#ffff\
ff\x22/>\x0a</svg>\x0a\
\x00\x00\x01\xd3\
<\
?xml version=\x221.\
0\x22 encoding=\x22UTF\
-8\x22?>\x0a<svg width\
=\x2216\x22 height=\x2216\
\x22 viewBox=\x220 0 1\
6 16\x22 fill=\x22none\
\x22 xmlns=\x22http://\
www.w3.org/2000/\
svg\x22>\x0a  <path d=\
\x22M8 0C5.8 0 4 1.\
8 4 4C4 6.2 5.8 \
8 8 8C10.2 8 12 \
6.2 12 4C12 1.8 \
10.2 0 8 0ZM8 6C\
6.9 6 6 5.1 6 4C\
6 2.9 6.9 2 8 2C\
9.1 2 10 2.9 10 \
4C10 5.1 9.1 6 8\
 6ZM14 12C14 10.\
3 11.3 9 8 9C4.7\
 9 2 10.3 2 12V1\
4C2 14.6 2.4 15 \
3 15H13C13.6 15 \
14 14.6 14 14V12\
ZM12 13H4V12C4 1\
1.2 6.7 11 8 11C\
9.3 11 12 11.2 1\
2 12V13Z\x22 fill=\x22\
#858585\x22/>\x0a</svg\
>\x0a\
\x00\x00\x01G\
<\
?xml version=\x221.\
0\x22 encoding=\x22UTF\
-8\x22?>\x0a<svg width\
=\x2216\x22 height=\x2216\
\x22 viewBox=\x220 0 1\
6 16\x22 fill=\x22none\
\x22 xmlns=\x22http://\
www.w3.org/2000/\
svg\x22>\x0a  <path d=\
\x22M14.5 2H9.5L8.5\
 1H3.5C2.67 1 2 \
1.67 2 2.5V13.5C\
2 14.33 2.67 15 \
3.5 15H14.5C15.3\
3 15 16 14.33 16\
 13.5V3.5C16 2.6\
7 15.33 2 14.5 2\
ZM14.5 13.5H3.5V\
4H14.5V13.5Z\x22 fi\
ll=\x22#ffffff\x22/>\x0a<\
/svg>\x0a\
\x00\x00\x01\x19\
<\
?xml version=\x221.\
0\x22 encoding=\x22UTF\
-8\x22?>\x0a<svg width\
=\x2216\x22 height=\x2216\
\x22 viewBox=\x220 0 1\
6 16\x22 fill=\x22none\
\x22 xmlns=\x22http://\
www.w3.org/2000/\
svg\x22>\x0a  <path d=\
\x22M2 2V6H6V2H2ZM1\
0 2V6H14V2H10ZM2\
 10V14H6V10H2ZM8\
 8H6V10H8V8ZM8 6\
H10V8H8V6ZM10 10\
V14H14V10H10ZM8 \
10H10V12H8V10Z\x22 \
fill=\x22#858585\x22/>\
\x0a</svg>\x0a\
\x00\x00\x01\xdc\
<\
?xml version=\x221.\
0\x22 encoding=\x22UTF\
-8\x22?>\x0a<svg width\
=\x2216\x22 height=\x2216\
\x22 viewBox=\x220 0 1\
6 16\x22 fill=\x22none\
\x22 xmlns=\x22http://\
www.w3.org/2000/\
svg\x22>\x0a  <path d=\
\x22M8 0.5C7.17 0.5\
 6.5 1.17 6.5 2V\
6.5H2C1.17 6.5 0\
.5 7.17 0.5 8S1.\
17 9.5 2 9.5H6.5\
V14C6.5 14.83 7.\
17 15.5 8 15.5S9\
.5 14.83 9.5 14V\
9.5H14C14.83 9.5\
 15.5 8.83 15.5 \
8S14.83 6.5 14 6\
.5H9.5V2C9.5 1.1\
7 8.83 0.5 8 0.5\
Z\x22 fill=\x22#ffffff\
\x22/>\x0a  <circle cx\
=\x2212\x22 cy=\x224\x22 r=\x22\
2\x22 fill=\x22#ffffff\
\x22/>\x0a  <circle cx\
=\x224\x22 cy=\x2212\x22 r=\x22\
2\x22 fill=\x22#ffffff\
\x22/>\x0a</svg>\x0a\
\x00\x00\x01G\
<\
?xml version=\x221.\
0\x22 encoding=\x22UTF\
-8\x22?>\x0a<svg width\
=\x2216\x22 height=\x2216\
\x22 viewBox=\x220 0 1\
6 16\x22 fill=\x22none\
\x22 xmlns=\x22http://\
www.w3.org/2000/\
svg\x22>\x0a  <path d=\
\x22M14.5 2H9.5L8.5\
 1H3.5C2.67 1 2 \
1.67 2 2.5V13.5C\
2 14.33 2.67 15 \
3.5 15H14.5C15.3\
3 15 16 14.33 16\
 13.5V3.5C16 2.6\
7 15.33 2 14.5 2\
ZM14.5 13.5H3.5V\
4H14.5V13.5Z\x22 fi\
ll=\x22#858585\x22/>\x0a<\
/svg>\x0a\
\x00\x00\x01\x19\
<\
?xml version=\x221.\
0\x22 encoding=\x22UTF\
-8\x22?>\x0a<svg width\
=\x2216\x22 height=\x2216\
\x22 viewBox=\x220 0 1\
6 16\x22 fill=\x22none\
\x22 xmlns=\x22http://\
www.w3.org/2000/\
svg\x22>\x0a  <path d=\
\x22M2 2V6H6V2H2ZM1\
0 2V6H14V2H10ZM2\
 10V14H6V10H2ZM8\
 8H6V10H8V8ZM8 6\
H10V8H8V6ZM10 10\
V14H14V10H10ZM8 \
10H10V12H8V10Z\x22 \
fill=\x22#ffffff\x22/>\
\x0a</svg>\x0a\
\x00\x00\x01\x9e\
<\
?xml version=\x221.\
0\x22 encoding=\x22UTF\
-8\x22?>\x0a<svg width\
=\x2216\x22 height=\x2216\
\x22 viewBox=\x220 0 1\
6 16\x22 fill=\x22none\
\x22 xmlns=\x22http://\
www.w3.org/2000/\
svg\x22>\x0a  <path d=\
\x22M15.7 13.3L11 8\
.6C11.6 7.7 12 6\
.6 12 5.5C12 2.5\
 9.5 0 6.5 0S1 2\
.5 1 5.5S3.5 11 \
6.5 11C7.6 11 8.\
7 10.6 9.6 10L14\
.3 14.7C14.7 15.\
1 15.3 15.1 15.7\
 14.7C15.9 14.3 \
15.9 13.7 15.7 1\
3.3ZM6.5 9C4.6 9\
 3 7.4 3 5.5S4.6\
 2 6.5 2S10 3.6 \
10 5.5S8.4 9 6.5\
 9Z\x22 fill=\x22#8585\
85\x22/>\x0a</svg>\x0a\
"

qt_resource_name = b"\
\x00\x05\
\x00o\xa6S\
\x00i\
\x00c\x00o\x00n\x00s\
\x00\x06\
\x07\xae\xc3\xc3\
\x00t\
\x00h\x00e\x00m\x00e\x00s\
\x00\x03\
\x00\x00j\xa3\
\x00c\
\x00s\x00s\
\x00\x10\
\x09=\xde\xc3\
\x00a\
\x00c\x00t\x00i\x00v\x00i\x00t\x00y\x00_\x00b\x00a\x00r\x00.\x00c\x00s\x00s\
\x00\x12\
\x03\xec4\x87\
\x00a\
\x00c\x00c\x00o\x00u\x00n\x00t\x00_\x00a\x00c\x00t\x00i\x00v\x00e\x00.\x00s\x00v\
\x00g\
\x00\x18\
\x02\x9b;\xc7\
\x00p\
\x00r\x00e\x00f\x00e\x00r\x00e\x00n\x00c\x00e\x00s\x00_\x00i\x00n\x00a\x00c\x00t\
\x00i\x00v\x00e\x00.\x00s\x00v\x00g\
\x00\x11\
\x02lM\x87\
\x00s\
\x00e\x00a\x00r\x00c\x00h\x00_\x00a\x00c\x00t\x00i\x00v\x00e\x00.\x00s\x00v\x00g\
\
\x00\x14\
\x0dW\x89\xe7\
\x00a\
\x00c\x00c\x00o\x00u\x00n\x00t\x00_\x00i\x00n\x00a\x00c\x00t\x00i\x00v\x00e\x00.\
\x00s\x00v\x00g\
\x00\x13\
\x0b\x92v\xe7\
\x00e\
\x00x\x00p\x00l\x00o\x00r\x00e\x00r\x00_\x00a\x00c\x00t\x00i\x00v\x00e\x00.\x00s\
\x00v\x00g\
\x00\x17\
\x0f\xeb\xef\xc7\
\x00e\
\x00x\x00t\x00e\x00n\x00s\x00i\x00o\x00n\x00s\x00_\x00i\x00n\x00a\x00c\x00t\x00i\
\x00v\x00e\x00.\x00s\x00v\x00g\
\x00\x16\
\x0a\xf7x'\
\x00p\
\x00r\x00e\x00f\x00e\x00r\x00e\x00n\x00c\x00e\x00s\x00_\x00a\x00c\x00t\x00i\x00v\
\x00e\x00.\x00s\x00v\x00g\
\x00\x15\
\x07\x99\xf9\x07\
\x00e\
\x00x\x00p\x00l\x00o\x00r\x00e\x00r\x00_\x00i\x00n\x00a\x00c\x00t\x00i\x00v\x00e\
\x00.\x00s\x00v\x00g\
\x00\x15\
\x00\xfb\x88\xe7\
\x00e\
\x00x\x00t\x00e\x00n\x00s\x00i\x00o\x00n\x00s\x00_\x00a\x00c\x00t\x00i\x00v\x00e\
\x00.\x00s\x00v\x00g\
\x00\x13\
\x0d\xae\x8a\xe7\
\x00s\
\x00e\x00a\x00r\x00c\x00h\x00_\x00i\x00n\x00a\x00c\x00t\x00i\x00v\x00e\x00.\x00s\
\x00v\x00g\
"

qt_resource_struct = b"\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x02\x00\x00\x00\x01\
\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x0a\x00\x00\x00\x05\
\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x10\x00\x02\x00\x00\x00\x01\x00\x00\x00\x03\
\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x22\x00\x02\x00\x00\x00\x01\x00\x00\x00\x04\
\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00.\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\
\x00\x00\x01\x987||\x90\
\x00\x00\x01\xcc\x00\x00\x00\x00\x00\x01\x00\x00\x15;\
\x00\x00\x01\x98#=\xb7\x80\
\x00\x00\x00\xb4\x00\x00\x00\x00\x00\x01\x00\x00\x0c/\
\x00\x00\x01\x98#=\xb7\x80\
\x00\x00\x00~\x00\x00\x00\x00\x00\x01\x00\x00\x0aO\
\x00\x00\x01\x98#=\xb7\x80\
\x00\x00\x00T\x00\x00\x00\x00\x00\x01\x00\x00\x08x\
\x00\x00\x01\x98#=\xb7\x80\
\x00\x00\x01\x9c\x00\x00\x00\x00\x00\x01\x00\x00\x13\xf0\
\x00\x00\x01\x98#=\xb7\x80\
\x00\x00\x01j\x00\x00\x00\x00\x00\x01\x00\x00\x12\x10\
\x00\x00\x01\x98#=\xb7\x80\
\x00\x00\x01\x0a\x00\x00\x00\x00\x00\x01\x00\x00\x0f\xa8\
\x00\x00\x01\x98#=\xb7\x80\
\x00\x00\x00\xdc\x00\x00\x00\x00\x00\x01\x00\x00\x0d\xd1\
\x00\x00\x01\x98#=\xb7\x80\
\x00\x00\x01\xfc\x00\x00\x00\x00\x00\x01\x00\x00\x16X\
\x00\x00\x01\x98#=\xb7\x80\
\x00\x00\x016\x00\x00\x00\x00\x00\x01\x00\x00\x10\xf3\
\x00\x00\x01\x98#=\xb7\x80\
"

def qInitResources():
    QtCore.qRegisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

def qCleanupResources():
    QtCore.qUnregisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

qInitResources()
