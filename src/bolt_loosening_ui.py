# lakshang
# evaluating bolt-loosening-via-digital-image-processing

import sys
import cv2
import glob
import math
import os
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk
from datetime import datetime

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

try:
    import ttk

    py3 = False
except ImportError:
    import tkinter.ttk as ttk

    py3 = True

from src import bolt_loosening_ui_support


def vp_start_gui():
    '''Starting point when module is the main routine.'''
    global val, w, root
    root = tk.Tk()
    top = BoltLooseningMain(root)
    bolt_loosening_ui_support.init(root, top)
    root.mainloop()


w = None


def create_BoltLooseningMain(root, *args, **kwargs):
    '''Starting point when module is imported by another program.'''
    global w, w_win, rt
    rt = root
    w = tk.Toplevel(root)
    top = BoltLooseningMain(w)
    bolt_loosening_ui_support.init(w, top, *args, **kwargs)
    return (w, top)


def destroy_BoltLooseningMain():
    global w
    w.destroy()
    w = None


class BoltLooseningMain:

    def browsefile(self):
        self.filename = filedialog.askopenfilename(initialdir="/", title="Select an Image File",
                                                   filetype=(("jpeg", "*.jpg"), ("png", "*.png")))
        cv_image = cv2.imread(self.filename)
        print(self.filename)

        # Setting the label with the location
        self.lblFileLocation.configure(text=self.filename)

        # Actual resize image
        self.acutal_image = cv2.resize(cv_image, (600, 700))

        b, g, r = cv2.split(cv_image)
        cv_image = cv2.merge((r, g, b))

        # Display the originally uploaded image
        cv_image = cv2.resize(cv_image, (330, 540))

        image = Image.fromarray(self.acutal_image)
        photo = ImageTk.PhotoImage(image)

        # Display the Orginal Image
        self.lblOriginalImg.configure(image=photo)
        self.lblOriginalImg.image = photo
        self.btnEdge.configure(state="active")

    def edgedetect(self):
        if(self.cmbBoltSize.current() == (-1)):
            messagebox.showerror("Error", "Please select the bolt size")
        elif(self.cmbPlateWidth.current() == -1):
            messagebox.showerror("Error", "Please select the steel palte size")
        else:
            gray = cv2.cvtColor(self.acutal_image, cv2.COLOR_RGB2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), cv2.BORDER_DEFAULT)
            self.canny = cv2.Canny(blur, 200, 300)

            # Display the canny image
            cv_image = cv2.resize(self.canny, (330, 540))

            image = Image.fromarray(self.canny)
            photo = ImageTk.PhotoImage(image)

            # Display the canny Image
            self.lblEdgeImg.configure(image=photo)
            self.lblEdgeImg.image = photo

            self.btnNut.configure(state="active")

    def boltnut(self):
        if (self.cmbBoltSize.current() == -1):
            messagebox.showerror("Error", "Please select the bolt size")
        elif (self.cmbPlateWidth.current() == -1):
            messagebox.showerror("Error", "Please select the steel palte size")
        else:
            template_data = []
            # make a list of all template images from a directory
            files1 = glob.glob('C:\\Users\\laksh\\PycharmProjects\\evaluating-bolt-loosening\\src\\template*.png')

            for myfile in files1:
                image = cv2.imread(myfile, 0)
                template_data.append(image)

            self.my_list = list()

            for tmp in template_data:
                (tH, tW) = tmp.shape[:2]
                # print('Height n Width of the the template image:', 'Height:', tH, 'Width:', tW)
                # cv2.imshow("Template", tmp)
                # cv2.waitKey(1000)
                # cv2.destroyAllWindows()
                result = cv2.matchTemplate(self.canny, tmp, cv2.TM_CCOEFF)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                top_left = max_loc
                bottom_right = (top_left[0] + tW, top_left[1] + tH)
                cv2.rectangle(self.canny, top_left, bottom_right, 255, 1)

                print('rec', top_left, bottom_right)

                self.my_list.insert(0, top_left)

                # Display the detection of nut and bolt
                cv_image = cv2.resize(self.canny, (330, 540))

                image = Image.fromarray(self.canny)
                photo = ImageTk.PhotoImage(image)

                # Display the detection of nut and bolt
                self.lblBoltNut.configure(image=photo)
                self.lblBoltNut.image = photo

                self.btnEvaluate.configure(state="active")

    def result(self):
        if (self.cmbBoltSize.current() == -1):
            messagebox.showerror("Error", "Please select the bolt size")
        elif (self.cmbPlateWidth.current() == -1):
            messagebox.showerror("Error", "Please select the steel palte size")
        else:
            cv2.line(self.canny, (self.my_list[1][0], self.my_list[1][1]), (self.my_list[0][0], self.my_list[0][1]), 255, 2)
            image = Image.fromarray(self.canny)
            photo = ImageTk.PhotoImage(image)

            # Display the detection of nut and bolt
            self.lblResult.configure(image=photo)
            self.lblResult.image = photo

            x = self.my_list[1][0] - self.my_list[0][0]
            y = self.my_list[1][1] - self.my_list[0][1]

            gap = (x * x) + (y * y)
            gap = math.sqrt(gap)
            print('Gap in Pixels', gap)
            print('Gap in Centimeters', (gap * 2.54 / 96))
            cm_value = (gap * 2.54 / 96)
            pixel_value = gap
            cv2.imwrite('final.png', self.canny)
            if gap > 84.0:
                # print('Bolt-loosening Detected')
                messagebox.showwarning("Warning", "Bolt-loosening detected ! | "+str(cm_value)+" cm bolt is loosened")
                self.report_txt(str(pixel_value), str(cm_value))
                self.reset_all()
            else:
                print('Bolt Fixed')
                messagebox.showinfo("Information", "Bolt is Fixed")
                self.report_txt(str(cm_value))

    def reset_all(self):
        self.btnEvaluate.configure(state="disabled")
        self.btnEdge.configure(state="disabled")
        self.btnNut.configure(state="disabled")
        self.lblFileLocation.configure(text="File Location")
        self.lblOriginalImg.configure(image='')
        self.lblEdgeImg.configure(image='')
        self.lblBoltNut.configure(image='')
        self.lblResult.configure(image='')

    def report_txt(self, value_pixel, value_cm):
        f = open("bolt_loosening_report.txt", "a")
        filename = os.path.split(self.filename)[1]
        dt = datetime.now()
        f.write(str(dt)+" | "+filename+" | " + value_pixel + " | " + value_cm + '\n')
        f.close()

    def __init__(self, top=None):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9'  # X11 color: 'gray85'
        _ana1color = '#d9d9d9'  # X11 color: 'gray85'
        _ana2color = '#ececec'  # Closest X11 color: 'gray92'
        self.style = ttk.Style()
        if sys.platform == "win32":
            self.style.theme_use('winnative')
        self.style.configure('.', background=_bgcolor)
        self.style.configure('.', foreground=_fgcolor)
        self.style.configure('.', font="TkDefaultFont")
        self.style.map('.', background=
        [('selected', _compcolor), ('active', _ana2color)])

        top.geometry("1365x680+287+105")
        top.title("Evaluating Bolt-loosening")
        top.configure(background="#d8ba27")
        top.configure(highlightbackground="#d9d9d9")
        top.configure(highlightcolor="black")

        self.openfileFrame = tk.LabelFrame(top)
        self.openfileFrame.place(relx=0.007, rely=0.015, relheight=0.081
                                 , relwidth=0.989)
        self.openfileFrame.configure(relief='groove')
        self.openfileFrame.configure(foreground="black")
        self.openfileFrame.configure(text='''Open an Image File''')
        self.openfileFrame.configure(background="#d9d9d9")
        self.openfileFrame.configure(highlightbackground="#d9d9d9")
        self.openfileFrame.configure(highlightcolor="#000000")
        self.openfileFrame.configure(width=1350)

        self.lblFileLocation = tk.Label(self.openfileFrame)
        self.lblFileLocation.place(relx=0.007, rely=0.364, height=21, width=543
                                   , bordermode='ignore')
        self.lblFileLocation.configure(activebackground="#f9f9f9")
        self.lblFileLocation.configure(activeforeground="black")
        self.lblFileLocation.configure(background="#d9d9d9")
        self.lblFileLocation.configure(disabledforeground="#a3a3a3")
        self.lblFileLocation.configure(foreground="#000000")
        self.lblFileLocation.configure(highlightbackground="#d9d9d9")
        self.lblFileLocation.configure(highlightcolor="black")
        self.lblFileLocation.configure(text='''File Location''')
        self.lblFileLocation.configure(width=543)

        self.btnBrowse = tk.Button(self.openfileFrame)
        self.btnBrowse.place(relx=0.437, rely=0.364, height=24, width=107
                             , bordermode='ignore')
        self.btnBrowse.configure(activebackground="#ececec")
        self.btnBrowse.configure(activeforeground="#000000")
        self.btnBrowse.configure(background="#d9d9d9")
        self.btnBrowse.configure(disabledforeground="#a3a3a3")
        self.btnBrowse.configure(foreground="#000000")
        self.btnBrowse.configure(highlightbackground="#d9d9d9")
        self.btnBrowse.configure(highlightcolor="black")
        self.btnBrowse.configure(pady="0")
        self.btnBrowse.configure(text='''Browse File''')
        self.btnBrowse.configure(command=self.browsefile)

        self.cmbBoltSize = ttk.Combobox(self.openfileFrame)
        self.cmbBoltSize.place(relx=0.622, rely=0.364, relheight=0.382
                               , relwidth=0.061, bordermode='ignore')
        self.value_list = [12]
        self.cmbBoltSize.configure(values=self.value_list)
        self.cmbBoltSize.configure(width=83)
        self.cmbBoltSize.configure(takefocus="")

        self.Label1 = tk.Label(self.openfileFrame)
        self.Label1.place(relx=0.548, rely=0.364, height=21, width=87
                          , bordermode='ignore')
        self.Label1.configure(background="#d9d9d9")
        self.Label1.configure(disabledforeground="#a3a3a3")
        self.Label1.configure(foreground="#000000")
        self.Label1.configure(text='''Select Bolt Size:''')

        self.Label1_1 = tk.Label(self.openfileFrame)
        self.Label1_1.place(relx=0.741, rely=0.364, height=21, width=147
                            , bordermode='ignore')
        self.Label1_1.configure(activebackground="#f9f9f9")
        self.Label1_1.configure(activeforeground="black")
        self.Label1_1.configure(background="#d9d9d9")
        self.Label1_1.configure(disabledforeground="#a3a3a3")
        self.Label1_1.configure(foreground="#000000")
        self.Label1_1.configure(highlightbackground="#d9d9d9")
        self.Label1_1.configure(highlightcolor="black")
        self.Label1_1.configure(text='''Select Steel Plate Width:''')
        self.Label1_1.configure(width=147)

        self.cmbPlateWidth = ttk.Combobox(self.openfileFrame)
        self.cmbPlateWidth.place(relx=0.859, rely=0.364, relheight=0.382
                                 , relwidth=0.061, bordermode='ignore')
        self.value_list = [1]
        self.cmbPlateWidth.configure(values=self.value_list)
        self.cmbPlateWidth.configure(takefocus="")

        self.Label1_3 = tk.Label(self.openfileFrame)
        self.Label1_3.place(relx=0.681, rely=0.364, height=21, width=27
                            , bordermode='ignore')
        self.Label1_3.configure(activebackground="#f9f9f9")
        self.Label1_3.configure(activeforeground="black")
        self.Label1_3.configure(background="#d9d9d9")
        self.Label1_3.configure(disabledforeground="#a3a3a3")
        self.Label1_3.configure(foreground="#000000")
        self.Label1_3.configure(highlightbackground="#d9d9d9")
        self.Label1_3.configure(highlightcolor="black")
        self.Label1_3.configure(text='''mm''')
        self.Label1_3.configure(width=27)

        self.Label1_4 = tk.Label(self.openfileFrame)
        self.Label1_4.place(relx=0.922, rely=0.364, height=21, width=17
                            , bordermode='ignore')
        self.Label1_4.configure(activebackground="#f9f9f9")
        self.Label1_4.configure(activeforeground="black")
        self.Label1_4.configure(background="#d9d9d9")
        self.Label1_4.configure(disabledforeground="#a3a3a3")
        self.Label1_4.configure(foreground="#000000")
        self.Label1_4.configure(highlightbackground="#d9d9d9")
        self.Label1_4.configure(highlightcolor="black")
        self.Label1_4.configure(text='''cm''')

        self.operationsFrame = tk.LabelFrame(top)
        self.operationsFrame.place(relx=0.007, rely=0.912, relheight=0.081
                                   , relwidth=0.989)
        self.operationsFrame.configure(relief='groove')
        self.operationsFrame.configure(font="-family {Segoe UI} -size 12 -weight bold -underline 1")
        self.operationsFrame.configure(foreground="black")
        self.operationsFrame.configure(text='''OPERATIONS''')
        self.operationsFrame.configure(background="#d9d9d9")
        self.operationsFrame.configure(highlightbackground="#d9d9d9")
        self.operationsFrame.configure(highlightcolor="black")
        self.operationsFrame.configure(width=1350)

        self.btnEdge = tk.Button(self.operationsFrame)
        self.btnEdge.place(relx=0.378, rely=0.364, height=24, width=74
                           , bordermode='ignore')
        self.btnEdge.configure(activebackground="#ececec")
        self.btnEdge.configure(activeforeground="#000000")
        self.btnEdge.configure(background="#d9d9d9")
        self.btnEdge.configure(disabledforeground="#a3a3a3")
        self.btnEdge.configure(foreground="#000000")
        self.btnEdge.configure(highlightbackground="#d9d9d9")
        self.btnEdge.configure(highlightcolor="black")
        self.btnEdge.configure(pady="0")
        self.btnEdge.configure(text='''Edge Detect''')
        self.btnEdge.configure(command=self.edgedetect)
        self.btnEdge.configure(state="disabled")

        self.btnNut = tk.Button(self.operationsFrame)
        self.btnNut.place(relx=0.459, rely=0.364, height=24, width=114
                          , bordermode='ignore')
        self.btnNut.configure(activebackground="#ececec")
        self.btnNut.configure(activeforeground="#000000")
        self.btnNut.configure(background="#d9d9d9")
        self.btnNut.configure(disabledforeground="#a3a3a3")
        self.btnNut.configure(foreground="#000000")
        self.btnNut.configure(highlightbackground="#d9d9d9")
        self.btnNut.configure(highlightcolor="black")
        self.btnNut.configure(pady="0")
        self.btnNut.configure(text='''Detect Nut & Bolt''')
        self.btnNut.configure(command=self.boltnut)
        self.btnNut.configure(state="disabled")

        self.btnEvaluate = tk.Button(self.operationsFrame)
        self.btnEvaluate.place(relx=0.585, rely=0.364, height=24, width=74
                               , bordermode='ignore')
        self.btnEvaluate.configure(activebackground="#ececec")
        self.btnEvaluate.configure(activeforeground="#000000")
        self.btnEvaluate.configure(background="#d80000")
        self.btnEvaluate.configure(disabledforeground="#a3a3a3")
        self.btnEvaluate.configure(font="-family {Segoe UI} -size 9 -weight bold")
        self.btnEvaluate.configure(foreground="#000000")
        self.btnEvaluate.configure(highlightbackground="#d9d9d9")
        self.btnEvaluate.configure(highlightcolor="#000000")
        self.btnEvaluate.configure(pady="0")
        self.btnEvaluate.configure(text='''Evaluate''')
        self.btnEvaluate.configure(command=self.result)
        self.btnEvaluate.configure(state="disabled")

        self.lblOriginalImg = tk.Label(top)
        self.lblOriginalImg.place(relx=0.007, rely=0.103, height=540, width=330)
        self.lblOriginalImg.configure(activebackground="#f9f9f9")
        self.lblOriginalImg.configure(activeforeground="black")
        self.lblOriginalImg.configure(background="#d9d9d9")
        self.lblOriginalImg.configure(disabledforeground="#a3a3a3")
        self.lblOriginalImg.configure(foreground="#000000")
        self.lblOriginalImg.configure(highlightbackground="#d9d9d9")
        self.lblOriginalImg.configure(highlightcolor="black")
        self.lblOriginalImg.configure(text='''Original Image''')

        self.lblEdgeImg = tk.Label(top)
        self.lblEdgeImg.place(relx=0.256, rely=0.103, height=540, width=330)
        self.lblEdgeImg.configure(activebackground="#f9f9f9")
        self.lblEdgeImg.configure(activeforeground="black")
        self.lblEdgeImg.configure(background="#d9d9d9")
        self.lblEdgeImg.configure(disabledforeground="#a3a3a3")
        self.lblEdgeImg.configure(foreground="#000000")
        self.lblEdgeImg.configure(highlightbackground="#d9d9d9")
        self.lblEdgeImg.configure(highlightcolor="black")
        self.lblEdgeImg.configure(text='''Edge Image''')

        self.lblBoltNut = tk.Label(top)
        self.lblBoltNut.place(relx=0.505, rely=0.103, height=540, width=330)
        self.lblBoltNut.configure(activebackground="#f9f9f9")
        self.lblBoltNut.configure(activeforeground="black")
        self.lblBoltNut.configure(background="#d9d9d9")
        self.lblBoltNut.configure(disabledforeground="#a3a3a3")
        self.lblBoltNut.configure(foreground="#000000")
        self.lblBoltNut.configure(highlightbackground="#d9d9d9")
        self.lblBoltNut.configure(highlightcolor="black")
        self.lblBoltNut.configure(text='''Identified Nut & Bolt''')

        self.lblResult = tk.Label(top)
        self.lblResult.place(relx=0.755, rely=0.103, height=540, width=330)
        self.lblResult.configure(activebackground="#f9f9f9")
        self.lblResult.configure(activeforeground="black")
        self.lblResult.configure(background="#d9d9d9")
        self.lblResult.configure(disabledforeground="#a3a3a3")
        self.lblResult.configure(foreground="#000000")
        self.lblResult.configure(highlightbackground="#d9d9d9")
        self.lblResult.configure(highlightcolor="black")
        self.lblResult.configure(text='''Result''')

    @staticmethod
    def popup1(event, *args, **kwargs):
        Popupmenu1 = tk.Menu(root, tearoff=0)
        Popupmenu1.configure(activebackground="#f9f9f9")
        Popupmenu1.configure(activeborderwidth="1")
        Popupmenu1.configure(activeforeground="black")
        Popupmenu1.configure(background="#d9d9d9")
        Popupmenu1.configure(borderwidth="1")
        Popupmenu1.configure(disabledforeground="#a3a3a3")
        Popupmenu1.configure(font="{Segoe UI} 9")
        Popupmenu1.configure(foreground="black")
        Popupmenu1.add_command(
            activebackground="#ececec",
            activeforeground="#000000",
            background="#d9d9d9",
            compound="left",
            font="TkMenuFont",
            foreground="#000000",
            label="NewCommand")
        Popupmenu1.add_command(
            activebackground="#ececec",
            activeforeground="#000000",
            background="#d9d9d9",
            compound="left",
            font="TkMenuFont",
            foreground="#000000",
            label="NewCommand")
        Popupmenu1.post(event.x_root, event.y_root)

    @staticmethod
    def popup2(event, *args, **kwargs):
        Popupmenu2 = tk.Menu(root, tearoff=0)
        Popupmenu2.configure(activebackground="#f9f9f9")
        Popupmenu2.configure(activeborderwidth="1")
        Popupmenu2.configure(activeforeground="black")
        Popupmenu2.configure(background="#d9d9d9")
        Popupmenu2.configure(borderwidth="1")
        Popupmenu2.configure(disabledforeground="#a3a3a3")
        Popupmenu2.configure(font="{Segoe UI} 9")
        Popupmenu2.configure(foreground="black")
        Popupmenu2.post(event.x_root, event.y_root)


if __name__ == '__main__':
    vp_start_gui()
