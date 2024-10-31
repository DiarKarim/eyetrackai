using UnityEngine;
using System.Collections;

public class CalibrationManager : MonoBehaviour
{
    [Tooltip("The Object we want to move through a path.")]
    [SerializeField] GameObject target;

    [Tooltip("The parent of the points they are under.")]
    [SerializeField] GameObject points;

    [Tooltip("The order of points we want the Target to follow.")]
    [SerializeField] Transform[] pathPoints;
    
    [Tooltip("How fast the target moves to points.")]
    [SerializeField] float speed = 2f;

    [Tooltip("How long should it stay at a point before moving to the next.")]
    [SerializeField] float delay = 0.5f;

    private int _currentPointIndex = 0;
    private bool _movingForward = true;
    private bool _isWaiting = false;

    void Update()
    {
        if (pathPoints.Length == 0 || target == null || _isWaiting) return;

        Vector3 targetPosition = target.transform.position;
        Vector3 destinationPosition = pathPoints[_currentPointIndex].position;

        target.transform.position = Vector3.MoveTowards(targetPosition, destinationPosition, speed * Time.deltaTime);

        if (Vector3.Distance(target.transform.position, destinationPosition) < 0.1f)
        {
            StartCoroutine(WaitAtPoint());
        }
    }

    private IEnumerator WaitAtPoint()
    {
        _isWaiting = true;
        yield return new WaitForSeconds(delay);

        if (_movingForward)
        {
            _currentPointIndex++;
            if (_currentPointIndex >= pathPoints.Length)
            {
                _currentPointIndex = pathPoints.Length - 2;
                _movingForward = false;
            }
        }
        else
        {
            _currentPointIndex--;
            if (_currentPointIndex < 0)
            {
                _currentPointIndex = 1;
                _movingForward = true;
            }
        }
        _isWaiting = false;
    }
    public void SetInvisible()
    {
        points.SetActive(!points.activeSelf); // Sets the visibility of the points if needed
    }
}
