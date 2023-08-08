# Code Review Format
- line number: comments


# Code Tracing Flow of `UI.py`
## L71: AnalysisThread_2D
Main class to calculate the performance of the object detector.

## L99: AnalysisThread_2D.run()
Main function for performance evaluation:
1. Read ground-truth annotations
2. Read detection results
3. Calculate evaluation metrics (e.g., TP, FP, FN ...)
4. Calculate final performance (e.g., ACC, FPR, FNR ...)

## L207: AnalysisThread_2D.BB2DEvaluation()
Main function to calculate evaluation metrics.
**It's the target function for code review.**


# UI.py
- L198: Why detected class ID would exceed the maximum GT class ID?
- L211: Is `nFP[self.class_num]` false positives in backgrond regions?
- L216: Why using `IOU_th = 0.15`?
- L245: Why adding the limitation of bbox center distance?
- L246-L261: Inefficient IOU calculation process.
- L272: 1 detection result might be matched to multiple ground-truths.
	```python
	# pseudo code of L208-L282
	matches = np.zeros(len(dts), dtype=bool) # default to False
	for gt in gts:
		for dt in dts:
			# find possible (gt, dt) pair with maximum IOU

		if gt is matched:
			matches[matched_dt] = True
			# Warning: we should comfirm the state of matches[matched_dt] before pairing (gt, matched_dt)
	```
- L273: What does `classRS == -1` mean? Why we match (gt, dt) & increase FN at the same time?
- L276-L280: The matching process is weird.
	```python
	# gt1: person
	# dt1: person
	# dt2: rider
	IOU(gt1, dt1) = 0.8
	IOU(gt1, dt2) = 0.9
	# Warning: (gt1, dt1) is the TP we want, 
	# and (gt1, dt1, dt2) should be counted as (TP, TP, FP).
	# But the current program matches (gt1, dt2) with higher IOU.
	# Therefore, (gt1, dt1, dt2) would be counted as (FN, FP, FP).
	```
- L279: If `classGT != classRS`, both FN & FP should be added by 1.
- L280: Is `hER` a partial confusion matrix that only calculates error predictions?
- L113: Does `self.lACC` equal to `TPR`?
- L114: The calculation of `self.lFPR = FP / GT = FP / (TP + FN)` is wrong. It should be `FP / (FP + TN)`. (Note: It's meaningless to define the number of true negatives of an object detection task, so we should NOT calculate FPR.)
- L133-L136: `FP[self.class_num]` (i.e., FP in background regions) is not accumulated to total sum.
- L71 & L292: What's the difference between `AnalysisThread_2D()` and `AnalysisDataSetThread_2D()`?


# UI_FP_analize.py
- L274: Why increasing TP when `classRS == -1`? It's different from the original implementation in `UI.py`.

