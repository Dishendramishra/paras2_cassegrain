# paras2_cassegrain
![paras2](https://user-images.githubusercontent.com/6905938/158105824-3d6c9a98-f061-4c36-a0c9-cd17335c7f8f.png)

### **Design Paradigms**

- **Qthread Tutorial using Qt Desinger**: https://www.youtube.com/watch?v=k5tIk7w50L4



### **System Configurations:**

Define an environment variable called `CASSEGRAIN_PORT`, which points to the port number of the arduino board connected to the system.



### Adding a new features:

1. Make required changes to the UI file `gui.ui` using Qt Designer.
2. Add business logic in the `main.pyw` file.
   1. make sure you have disabled the button in `disable_buttons()`.
   2. Implement a function with desired functionality  and connect it to the button.
3. Add supporting function calls in the arduino sketch `paras2_cassegrain.ino`



### **Development Resources:**

- **Qt Desinger** : https://build-system.fman.io/qt-designer-download
- **VS Code** : https://code.visualstudio.com/download
- **Python 3.7.9** : https://www.python.org/downloads/release/python-379/
- **Arduino IDE** : https://www.arduino.cc/en/software 