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
            // EditorUtility.SetDirty(calibrationManager.gameObject);
            // PrefabUtility.SavePrefabAsset(calibrationManager.gameObject);
        }
    }
}
