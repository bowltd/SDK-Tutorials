#include "display.h"

int main(void) {

    Display display;
    std::vector<DisplayInfo> list;
    list.push_back(DisplayInfo("heads",0.0,1.0,0.5));
    list.push_back(DisplayInfo("shoulders",0.0,1.0,0.75));
    list.push_back(DisplayInfo("knees",0.0,3.0,0.75));
    list.push_back(DisplayInfo("and",1.0,2.0,1.5));
    list.push_back(DisplayInfo("toes",1.0,2.0,1.5));
    list.push_back(DisplayInfo("eyes",1.0,2.0,1.5));
    list.push_back(DisplayInfo("ears",1.0,2.0,1.5));
    list.push_back(DisplayInfo("mouth",1.0,2.0,1.5));
    list.push_back(DisplayInfo("and",1.0,2.0,1.5));
    list.push_back(DisplayInfo("nose",1.0,2.0,1.5));

    display.list = list;
    display.Run();
}