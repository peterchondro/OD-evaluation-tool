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
	```text
	Detected class ID surpassing the maximum GT class ID
 	is often due to differing class lists in ground truth and predictions.
	```
- L211: Is `nFP[self.class_num]` false positives in backgrond regions?
	```text
	This containment was designed for a 3D object detector,
 	which initially lacked any classes at that time.
	```
- L216: Why using `IOU_th = 0.15`?
	```text
	This is a parameter, the value corresponds to TP/FP/FN.
	```
- L245: Why adding the limitation of bbox center distance?
	```text
	This measure was essential for comprehensive evaluation in both 2D and 3D contexts.
 	Regarding the rationale of our previous manager, I don't recall;
 	you could inquire with him directly.
	```
- L246-L261: Inefficient IOU calculation process.
	```text
	To facilitate 3D evaluation, we introduced this IoU calculation method.
 	Additionally, during development, computational cost was not a primary consideration.
	```
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
	-
	```text
	Feel free to test this with your own data to verify
 	if TP/FP/FN align with your expectations.
 	Alternatively, consider refining this section if needed.
	```
- L273: What does `classRS == -1` mean? Why we match (gt, dt) & increase FN at the same time?
	```text
	classRS = -1 is related to no-class class in 3D.
	```
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
	-
	```text
	In this specific example, both TP and FP are consistently 1,
 	regardless of the specific scenario (Assuming IoU_th @ 0.5).
	```
- L279: If `classGT != classRS`, both FN & FP should be added by 1.
	```text
	Initially, FP was incremented by 1, but this was later removed.
 	For further clarification, it would be advisable to consult the previous manager.
	```
- L280: Is `hER` a partial confusion matrix that only calculates error predictions?
	```text
	Yes
	```
- L113: Does `self.lACC` equal to `TPR`?
	```text
	Yes
	```
- L114: The calculation of `self.lFPR = FP / GT = FP / (TP + FN)` is wrong. It should be `FP / (FP + TN)`. (Note: It's meaningless to define the number of true negatives of an object detection task, so we should NOT calculate FPR.)
	```text
	Indeed, the equation employed there differs from the conventional FPR.
 	It's recommended to engage in a conversation with the previous manager to delve into this.
 	However, if I may contribute, the inclusion of FPR calculation appears to stem from
 	the significance attributed to the false alarm rate in the 2017 MOEA proposal.
 	This emphasis translated into the utilization of FPR as a metric.
	```
- L133-L136: `FP[self.class_num]` (i.e., FP in background regions) is not accumulated to total sum.
	```text
	This component is excluded from the final 2D calculation.
	```
- L71 & L292: What's the difference between `AnalysisThread_2D()` and `AnalysisDataSetThread_2D()`?
	```text
	To clarify, AnalysisThread_2D() is designed for analyzing individual images,
 	while AnalysisDataSetThread_2D() serves the purpose of analyzing multiple images
 	or batches collectively.
	```

# UI_FP_analize.py
- L274: Why increasing TP when `classRS == -1`? It's different from the original implementation in `UI.py`.

