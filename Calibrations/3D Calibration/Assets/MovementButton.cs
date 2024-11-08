using System.Collections;
using System.Collections.Generic;
using TMPro;
using UnityEngine;
using UnityEngine.UI;

public class MovementButton : MonoBehaviour
{
    [SerializeField] CalibrationManager calibrationManager;
    [SerializeField] TextMeshProUGUI textBox;

    private void Update()
    {
        if (calibrationManager != null)
        {
            if (calibrationManager._isMoving)
            {
                textBox.text = "Stop Movement";
            }
            else
            {
                textBox.text = "Start Movement";
            }
        }
    }
}
