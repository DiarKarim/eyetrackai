using UnityEditor;
using UnityEngine;

[CustomEditor(typeof(CalibrationManager))]
public class CalibrationManagerEditor : Editor
{
    public override void OnInspectorGUI()
    {
        DrawDefaultInspector();

        CalibrationManager calibrationManager = (CalibrationManager)target;
        if (GUILayout.Button("Set Point Visibility"))
        {
            calibrationManager.SetInvisible();
        }

        

        EditorGUI.BeginDisabledGroup(!Application.isPlaying);
        if (GUILayout.Button(calibrationManager._isMoving ? "Stop Movement" : "Start Movement"))
        {
            calibrationManager.ToggleMovement();
        }
        
        if (GUILayout.Button("Reset")) 
        { 
            calibrationManager.Reset(); 
        }
        EditorGUI.EndDisabledGroup();
    }
}
