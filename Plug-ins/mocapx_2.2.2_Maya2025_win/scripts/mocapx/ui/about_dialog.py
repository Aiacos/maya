# -*- coding: utf-8 -*-
import mocapx
# pylint: disable=no-name-in-module
# noinspection PyUnresolvedReferences
from mocapx.vendor.Qt import QtWidgets, QtCore, QtGui
from mocapx.lib.uiutils import scaled, get_maya_window
from mocapx.ui.widgets import ToolButton

WEBSITE_LINK = "http://mocapx.com"
APP_STORE_LINK = "https://itunes.apple.com/cz/app/mocapx/id1426530589?mt=8"


class AboutDialog(QtWidgets.QDialog):
    # noinspection SpellCheckingInspection
    def __init__(self, width=scaled(600), height=scaled(600), parent=get_maya_window()):
        super(AboutDialog, self).__init__(parent)

        self.setWindowTitle("About MocapX")
        self.setFixedSize(width, height)
        self.setModal(True)

        main_margin = scaled(10)

        # logo area
        label_logo = QtWidgets.QLabel()
        image = QtGui.QPixmap("{}/icons/{}".format(mocapx.plugin_distr_root, "MCPXLogo.svg"))
        label_logo.setPixmap(image)
        logo_area = QtWidgets.QFrame()
        logo_area.setStyleSheet("QFrame {background-color: rgb(240, 240, 240)}")
        logo_area.setFixedSize(self.width() - main_margin * 2, image.height() + scaled(20))
        logo_layout = QtWidgets.QVBoxLayout()
        logo_layout.setContentsMargins(scaled(0), scaled(0), scaled(0), scaled(0))
        logo_layout.setSpacing(scaled(6))
        logo_layout.addWidget(label_logo)
        logo_layout.setAlignment(label_logo, QtCore.Qt.AlignCenter)
        logo_area.setLayout(logo_layout)

        # version info
        version_label = QtWidgets.QLabel("MocapX Maya plug-in {}".format(mocapx.version))

        # header text
        text = """
Copyright(c) 2019 Techapp s.r.o.
All rights reserved

Developers: Alexey Denisenko, Artem Karpinsky, Maria Endicott, Michal Klement, Daniel Brezina,
Jan Vrabel, Ondrej Pridal

Head Rig: Igor Sysoev
        """
        text_label = QtWidgets.QLabel(text)

        # website link
        link_label = QtWidgets.QLabel(
            "<a href=\"{0}/\"><span style=\" font-size:9pt; "
            "font-weight:600; text-decoration: underline; color:#43aab5;\">{0}/</span></a>".format(
                WEBSITE_LINK))
        link_label.setTextFormat(QtCore.Qt.RichText)
        link_label.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        link_label.setOpenExternalLinks(True)

        # AppStore link, icon size: 135, 40 108, 32
        icon_path = 'MCPXAppStore'
        download_button = ToolButton(
            size=(scaled(135), scaled(40)),
            icon_name=icon_path,
            highlighted_icon=icon_path,
            alpha=True
        )
        download_button.set_hover_cursor(QtCore.Qt.PointingHandCursor)

        # text area
        text_browser = QtWidgets.QTextBrowser()
        text = """
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8pt; font-weight:400; font-style:normal;">
<p align="center" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Circular Pro Book'; font-size:xx-large;">Terms &amp; Conditions</span></p>
<p style=" margin-top:14px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Circular Pro Book'; font-size:large;">1. PROCESSING AND PROTECTION OF PERSONAL DATA</span></p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Circular Pro Book'; font-size:medium;">The company Techapp s.r.o.(hereinafter referred to as Techapp) in connection with the adoption of Regulation (EU) 2016/679 of the European Parliament and of the Council of 27 April 2016 on the protection of natural persons with regard to the processing of personal data and on the free movement of such data, and repealing Directive 95/46/ES (GDPR), which applies to the processing of personal data with effect from 25 May 2018, hereby declares that any handling of personal data of natural persons collected by Techapp in the course of conducting its business is in full compliance with applicable laws (primarily the above-stated Regulation and Act 101/2000 Coll., on the Protection of Personal Data).</span></p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Circular Pro Book'; font-size:medium;"> </span></p>
<p style=" margin-top:14px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Circular Pro Book'; font-size:large;">2. PRINCIPLES FOR THE COLLECTION AND PROCESSING OF PERSONAL DATA</span></p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Circular Pro Book'; font-size:medium;">The company Techapp s.r.o.(hereinafter referred to as Techapp) in connection with the adoption of Regulation (EU) 2016/679 of the European Parliament and of the Council of 27 April 2016 on the protection of natural persons with regard to the processing of personal data and on the free movement of such data, and repealing Directive 95/46/ES (GDPR), which applies to the processing of personal data with effect from 25 May 2018, hereby declares that any handling of personal data of natural persons collected by Techapp in the course of conducting its business is in full compliance with applicable laws (primarily the above-stated Regulation and Act 101/2000 Coll., on the Protection of Personal Data).</span></p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Circular Pro Book'; font-size:medium;">The company Techapp s.r.o.(hereinafter referred to as Techapp) in connection with the adoption of Regulation (EU) 2016/679 of the European Parliament and of the Council of 27 April 2016 on the protection of natural persons with regard to the processing of personal data and on the free movement of such data, and repealing Directive 95/46/ES (GDPR), which applies to the processing of personal data with effect from 25 May 2018, hereby declares that any handling of personal data of natural persons collected by Techapp in the course of conducting its business is in full compliance with applicable laws (primarily the above-stated Regulation and Act 101/2000 Coll., on the Protection of Personal Data).</span></p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Circular Pro Book'; font-size:medium;"> </span></p>
<p style=" margin-top:14px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Circular Pro Book'; font-size:large;">3. CONTACT INFORMATION</span></p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Circular Pro Book'; font-size:medium;">The company Techapp s.r.o.(hereinafter referred to as Techapp) in connection with the adoption of Regulation (EU) 2016/679 of the European Parliament and of the Council of 27 April 2016 on the protection of natural persons with regard to the processing of personal data and on the free movement of such data, and repealing Directive 95/46/ES (GDPR), which applies to the processing of personal data with effect from 25 May 2018, hereby declares that any handling of personal data of natural persons collected by Techapp in the course of conducting its business is in full compliance with applicable laws (primarily the above-stated Regulation and Act 101/2000 Coll., on the Protection of Personal Data).</span></p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Circular Pro Book'; font-size:medium;">The company Techapp s.r.o.(hereinafter referred to as Techapp) in connection with the adoption of Regulation (EU) 2016/679 of the European Parliament and of the Council of 27 April 2016 on the protection of natural persons with regard to the processing of personal data and on the free movement of such data, and repealing Directive 95/46/ES (GDPR), which applies to the processing of personal data with effect from 25 May 2018, hereby declares that any handling of personal data of natural persons collected by Techapp in the course of conducting its business is in full compliance with applicable laws (primarily the above-stated Regulation and Act 101/2000 Coll., on the Protection of Personal Data).</span></p>
<p style="-qt-paragraph-type:empty; margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'Circular Pro Book'; font-size:medium;"><br /></p>
<p align="center" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Circular Pro Book'; font-size:xx-large;">Privacy policy</span></p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Circular Pro Book'; font-size:10pt;">1. GENERAL TERMS AND CONDITIONS FOR THE USE OF MOCAPX SERVICES</span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Circular Pro Book'; font-size:medium;">The company TECHAPP s.r.o., with headquarters at Korunní 810/104, 101 00 Vinohrady Prague 10, Czech Republic (hereinafter referred to as the Provider) is an authorized provider of the virtual service MocapX. The following terms and conditions apply to users of this service.</span></p>
<p style="-qt-paragraph-type:empty; margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'Circular Pro Book'; font-size:medium;"><br /></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Circular Pro Book'; font-size:10pt;">2. ANIMATION APPLICATION PLUG-IN MocapX</span></p>
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'Circular Pro Book'; font-size:medium;"><br /></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Circular Pro Book'; font-size:medium;">The MocapX plug-in is software that allows users to proces data from the MocapX mobile application (pro and lite versions). The main features of the plug-in are: Support for converting recording data into clips reading clips from the clip reader creating a library of poses/expressions ( selection of controls with different values ) synchronising video with a timeline using the embeded player plug-in is made to be used with Autodesk Maya</span></p>
<p style="-qt-paragraph-type:empty; margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'Circular Pro Book'; font-size:medium;"><br /></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Circular Pro Book'; font-size:10pt;">3. USING THE PLUG-IN</span></p>
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'Circular Pro Book'; font-size:medium;"><br /></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Circular Pro Book'; font-size:medium;">The plug-in is provided to authorized users of the MocapX animation application and is available for download on the Provider’s website www.mocapx.com free of charge. Authorized users of the animation application MocapX are to use the downloaded plug-in in accordance with the specifications of the given software and version. This will extend the functionality of the application to include the required features. The User can then work with the object intended for animation in accordaqnce with the technical specifications. The User bears all responsibility for the use of the animation application in connection with the plug-in and for the end result. In order to use the plug-in service, user registration is required.</span></p>
<p style="-qt-paragraph-type:empty; margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'Circular Pro Book'; font-size:medium;"><br /></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Circular Pro Book'; font-size:10pt;">4. USER AND PROVIDER RIGHTS AND OBLIGATIONS</span></p>
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'Circular Pro Book'; font-size:medium;"><br /></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Circular Pro Book'; font-size:medium;">The User bears sole responsibility for the content and form of the object intended for animation. The User acknowledges that the licensing rights for the plug-in belong exclusively to the Provider. The Provider authorizes the User to download and use the plug-in for its intended purpose only – extending the functionality of the animation application. By downloading the plug-in, the Provider provides the User with only a limited, non-exclusive, revocable and non-transferable license to use the plug-in for the designated purpose. The User is not authorized to use the plug-in for any other purpose than that designated by the Provider; specifically, the User may not copy, distribute, modify or interfere with the source code of the plug-in. The Provider is not (in accordance with the provisions in § 6 Act No. 480/2004 Coll., on certain Information Society Services as amended) obliged to supervise the content of the transferred or stored information (objects or other data), nor is the Provider obliged to actively seek out facts and circumstances indicating the illegal nature of the content stored by the User. The Provider does not conduct any verification of the legitimacy or illegitimacy of the animation work performed by the User with the animation object, in particular, the Provider does not bear any responsibility for the User’s handling of the animation object in accordance with copyright law. The Provider does not guarantee the functionality of the plug-in and the User undertakes to use the plug-in at his/her own risk in accordance with these terms and conditions. The Provider shall not be held liable for any damage or harm incurred during the use of the plug-in. The User acknowledges and agrees that the Provider is authorized to perform changes to the plug-in at any time and in any manner, including the functionality of the plug-in, the scope and conditions of use, or withdraw permission to use the plug-in, without notifying the User. The Provider is not bound to any guarantees pertaining to the plug-in, namely guarantees regarding the functionality and availability of the plug-in. The User acknowledges that the use of the Provider’s plug-in module does not come with any guarantees and that use is thus associated with a certain degree of risk. The User accepts this risk. The Provider shall not be held liable for any direct or indirect damage incurred by the User in connection to the use of the Provider’s plug-in. The Provider shall not be held liable for any malfunctions, unavailability, poor access or speed of any service or any loss of the object or information, either whole or in part, connected to the use of the plug-in. The User acknowledges and expressly consents to third-party advertising being displayed during the use of the plug-in. The User hereby expresses his/her consent to being added to the Provider’s mailing list for promotional purposes. The User may unsubscribe from these e-mails at any time.</span></p>
<p style="-qt-paragraph-type:empty; margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'Circular Pro Book'; font-size:medium;"><br /></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Circular Pro Book'; font-size:10pt;">5. PROTECTION OF PERSONAL DATA</span></p>
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'Circular Pro Book'; font-size:medium;"><br /></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Circular Pro Book'; font-size:medium;">The Provider undertakes to protect information and personal data obtained from Users in accordance with legal regulations. The User’s personal data is processed only to the extent necessary for the provision of the plug-in for the purpose of providing services and for communication between the Provider and User, in accordance with Regulation (EU) 2016/679 of the European Parliament and Council of 27 April 2016 on the protection of natural persons with regard to the processing of personal data and on the free movement of such data, and repealing Directive 95/46/ES (GDPR) and with Act 101/2000 Coll., on the Protection of Personal Data. The personal data of individual users is processed in an automated manner electronically. Details regarding the protection of personal data can be found here (link to the document titled PROCESSING AND PROTECTION OF PERSONAL DATA).</span></p>
<p style="-qt-paragraph-type:empty; margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'Circular Pro Book'; font-size:medium;"><br /></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Circular Pro Book'; font-size:10pt;">6. FINAL PROVISIONS</span></p>
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'Circular Pro Book'; font-size:medium;"><br /></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Circular Pro Book'; font-size:medium;">These terms and conditions and the relationship between the Provider and the User are governed by Czech law. The Provider reserves the right to modify these terms and conditions at any time. The changes made to these terms and conditions take effect on the date specified by the Provider.</span></p></body></html>
"""
        text_browser.setHtml(text)

        # button
        ok_button = QtWidgets.QPushButton("OK")
        ok_button.setFixedWidth(scaled(75))

        # layout
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(
            main_margin, main_margin, main_margin, main_margin)
        main_layout.setSpacing(scaled(6))
        main_layout.addWidget(logo_area)
        main_layout.addItem(
            QtWidgets.QSpacerItem(scaled(1), scaled(8), QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        )
        main_layout.addWidget(version_label)
        main_layout.addWidget(text_label)
        main_layout.addWidget(link_label)
        main_layout.addWidget(download_button)
        main_layout.addWidget(text_browser)
        main_layout.addWidget(ok_button)
        main_layout.setAlignment(ok_button, QtCore.Qt.AlignCenter)
        self.setLayout(main_layout)

        # handlers
        ok_button.clicked.connect(self.close)
        download_button.clicked.connect(lambda: QtGui.QDesktopServices.openUrl(APP_STORE_LINK))
