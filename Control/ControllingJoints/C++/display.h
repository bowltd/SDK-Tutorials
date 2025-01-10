#include <curses.h>
#include <vector>
#include <string>
#include <cmath>
using namespace std;

class DisplayInfo{
public:    
    
    string Name;
    char* NameChar;
    float Value, ValueMax, ValueMin;
    
    DisplayInfo(string name, float valueMin, float valueMax, float value){
        Name = name;
        ValueMin = valueMin;
        ValueMax = valueMax;
        SetValue(value);
        SetName(10);
    }

    void SetValue(float v){
        Value = v;
        if (Value<ValueMin){ Value = ValueMin;}
        if (Value>ValueMax){ Value = ValueMax;}
    }

    void SetName(int length){ 
        NameChar = (char*)malloc(sizeof(char)*(length));
        for (int i=0;i<length;i++){
            NameChar[i] = (char)Name[i];
        }
    }
    
    const char* GetValue(int length) { 
        return to_string(Value).substr(0,length).c_str(); 
    }
    
    const char* GetBar(int length){
        float prop = (Value - ValueMin) / (ValueMax - ValueMin);
        int j = round(prop * (length-1));
        char * s = (char*)malloc(sizeof(char)*(length+2));
        s[0]='|';
        for (int i=0;i<length;i++){
            if (i==j){
                s[i+1]= '!';
            } else {
                s[i+1]='.';
            }
        }
        s[length+1] = '|';
        return s;
    }
};


class Display{
    public:
    WINDOW * mainwin, * content;
    int ch, height, width, listStart, listFlankers;

    std::vector<DisplayInfo> list;
    int listIndex;
    float increment = 0.05;

    Display(){
        if ( (mainwin = initscr()) == NULL ) {
           fprintf(stderr, "Error initialising ncurses.\n");
           exit(EXIT_FAILURE);
        }
        height = 15;
        width = 50;
        listStart = 4;
        listIndex = 0;
        listFlankers = 3;
        noecho();
        keypad(mainwin, TRUE);
        content = subwin(mainwin, height, width, 1, 5);
        Update();
    }

    void Update(){
        wclear(content);
        mvwaddstr(content, 2, 2, "Joints:");
        int org = listIndex - listFlankers;
        if (org<0){ org = 0;}       
        int end = org + 2*listFlankers + 1;
        if (end>=list.size()){ end = list.size();}
        org = end - 2*listFlankers-1;
        if (org<0){ org = 0; }       
        int j=listStart;
        for(int i=org;i<end;i++){
            if(i==listIndex){
                mvwaddstr(content,j,2,"*");
            }
            mvwaddstr(content,j,5,list[i].NameChar);
            mvwaddstr(content,j,20,list[i].GetBar(11));
            mvwaddstr(content,j,40,list[i].GetValue(6));
            j++;        
        }
        box(content, 0, 0);
        mvwaddstr(content, 0, 2, " BOW Tutorial ");
        mvwaddstr(content, height-1, 2, " use arrow keys, or 'q' to quit ");
    }

    void Run(){
        Update();
        while ((ch = getch()) != 'q' ) {
        switch ( ch ) {
            case KEY_DOWN:
                if (listIndex < list.size()-1){ listIndex++;}
                break;
            case KEY_UP:
                if (listIndex > 0){ listIndex--;}
                break;
            case KEY_LEFT:
                list[listIndex].SetValue(list[listIndex].Value - increment);
                SetCurrentJoint();
                break;
            case KEY_RIGHT:
                 list[listIndex].SetValue(list[listIndex].Value + increment);
                 SetCurrentJoint();
                break;
            }
            Update();
            wrefresh(content);
        }
    }

    void SetCurrentJoint(){
        return;
    }

    ~Display(){
        delwin(content);
        delwin(mainwin);
        endwin();
        refresh();
    }
};
