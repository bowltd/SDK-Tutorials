using System;
using System.Numerics;
using Mindmagma.Curses;

class DisplayInfo {
	public string Name;
	public float Value, ValueMax, ValueMin;
	public DisplayInfo(string name, float valueMin, float valueMax, float value){
		Name = name;
		ValueMin = valueMin;
		ValueMax = valueMax;
		SetValue(value);
	}

	public void SetValue(float v){
        Value = v;
        if (Value<ValueMin){ Value = ValueMin;}
        if (Value>ValueMax){ Value = ValueMax;}
    }

    public string GetValue(int length){
    	string value = Value.ToString();
    	return value.Length <= length ? value : value.Substring(0, length);
    }

    public string GetBar(int length){
        float prop = (Value - ValueMin) / (ValueMax - ValueMin);
        int j = (int)Math.Round(prop * (length-1));
		string s = "|";
	   	for (int i=0; i<length; i++){
	   		if (i==j){
	   			s+="!";
	   		} else {
	   			s+=".";
	   		}
	   	}
	   	return s+"|";
	}
}

class Display{

	public IntPtr mainwin, content;
	public int ch, height, width, listStart, listFlankers, listIndex;
	public List<DisplayInfo> list;
	public float increment = 0.05f;

	public Display(){
		mainwin = NCurses.InitScreen();
		height = 15;
	    width = 50;
	    listStart = 4;
	    listIndex = 0;
	    listFlankers = 3;
		NCurses.NoEcho();
		NCurses.Keypad(mainwin,true);
		content = NCurses.SubWindow(mainwin, height, width, 1, 5);
		list = new List<DisplayInfo>();
		Update();
	}

	public void Update(){
		NCurses.ClearWindow(content);
		NCurses.MoveWindowAddString(content, 2, 2, "Joints:");
		
		int org = listIndex - listFlankers;
        if (org<0){ org = 0;}       
        int end = org + 2*listFlankers + 1;
        if (end>=list.Count){ end = list.Count;}
        org = end - 2*listFlankers-1;
        if (org<0){ org = 0; }       
        int j=listStart;
        for(int i=org;i<end;i++){
            if(i==listIndex){
                NCurses.MoveWindowAddString(content,j,2,"*");
            }
            NCurses.MoveWindowAddString(content,j,5,list[i].Name);
            NCurses.MoveWindowAddString(content,j,20,list[i].GetBar(11));
            NCurses.MoveWindowAddString(content,j,40,list[i].GetValue(6));
            j++;        
        }

		NCurses.Box(content,'|','-');
		NCurses.MoveWindowAddString(content, 0 ,2, " BOW Tutorial ");
		NCurses.MoveWindowAddString(content, height-1 ,2, " use arrow keys, or 'q' to quit ");
	}

	public void Run(){
		Update();
		while ((ch = NCurses.GetChar())!='q'){
			switch ( ch ) {
            	case CursesKey.DOWN:
            	    if (listIndex < list.Count-1){ listIndex++;}
            	    break;
             	case CursesKey.UP:
                 	if (listIndex > 0){ listIndex--;}
                 	break;
            	case CursesKey.LEFT:
                 	list[listIndex].SetValue(list[listIndex].Value - increment);
            		SetCurrentJoint();
            		break;
            	case CursesKey.RIGHT:
            	     list[listIndex].SetValue(list[listIndex].Value + increment);
            	     SetCurrentJoint();
            	     break;
            }
			Update();
			NCurses.WindowRefresh(content);
		}
		NCurses.ClearWindow(content);
        NCurses.Echo();
        NCurses.Keypad(mainwin,false);
        NCurses.Refresh();
        NCurses.EndWin();
	}

	public virtual void SetCurrentJoint(){
        return;
    }
}