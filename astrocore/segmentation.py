# astrocore/segmentation.py

import numpy as np


class TimeSeriesSegmentation:
    """
    Segment a time series into continuous chunks using cadence gaps.

    Parameters
    ----------
    gap_factor : float, optional
        A gap is declared when the time difference between two
        consecutive points exceeds:

            gap_factor * median_cadence

        Default is 5.
    """

    def __init__(self, gap_factor=5):

        self.gap_factor = gap_factor

    def run(self, lightcurve):
        """
        Segment a light curve and compute diagnostic metadata.

        Parameters
        ----------
        lightcurve : dict
            Standard astrocore lightcurve dictionary:

            {
                "t": ...,
                "y": ...,
                "meta": ...
            }

        Returns
        -------
        dict
            Segmentation result containing chunks, gaps,
            and summary statistics.
        """

        t = lightcurve["t"]
        y = lightcurve["y"]

        if len(t) < 2:

            raise ValueError(
                "At least two data points are required."
            )

        dt = np.diff(t)

        median_cadence = np.median(dt)

        gap_indices = np.where(
            dt > self.gap_factor * median_cadence
        )[0]

        boundaries = np.concatenate(
            (
                [-1],
                gap_indices,
                [len(t) - 1]
            )
        )

        total_points = len(t)

        total_duration = t[-1] - t[0]

        chunks = []

        for chunk_id, (start, end) in enumerate(
            zip(boundaries[:-1], boundaries[1:])
        ):

            start_idx = start + 1
            end_idx = end + 1

            chunk_t = t[start_idx:end_idx]
            chunk_y = y[start_idx:end_idx]

            start_time = chunk_t[0]
            end_time = chunk_t[-1]

            duration = (
                end_time - start_time
                if len(chunk_t) > 1
                else 0.0
            )

            center_time = (
                start_time + end_time
            ) / 2

            relative_position = (
                (center_time - t[0])
                / total_duration
                if total_duration > 0
                else 0.0
            )

            chunks.append(
                {
                    "chunk_id": chunk_id,
                    "t": chunk_t,
                    "y": chunk_y,
                    "length": len(chunk_t),
                    "duration": duration,
                    "start_time": start_time,
                    "end_time": end_time,
                    "start_index": start_idx,
                    "end_index": end_idx,
                    "center_time": center_time,
                    "relative_position": relative_position,
                    "fraction_of_dataset":
                        len(chunk_t) / total_points
                }
            )

        gaps = []

        if len(chunks) > 1:

            for i in range(len(chunks) - 1):

                gap_duration = (
                    chunks[i + 1]["start_time"]
                    - chunks[i]["end_time"]
                )

                gaps.append(
                    {
                        "gap_id": i,
                        "from_chunk": i,
                        "to_chunk": i + 1,
                        "duration": gap_duration
                    }
                )

        chunk_lengths = [
            chunk["length"]
            for chunk in chunks
        ]

        gap_lengths = [
            gap["duration"]
            for gap in gaps
        ]

        summary = {
            "n_chunks": len(chunks),
            "n_gaps": len(gaps),
            "total_points": total_points,
            "total_duration": total_duration,
            "median_cadence": median_cadence,
            "largest_chunk": max(chunk_lengths),
            "smallest_chunk": min(chunk_lengths),
            "fraction_in_largest_chunk":
                max(chunk_lengths) / total_points
        }

        if len(gap_lengths) > 0:

            summary["largest_gap"] = max(gap_lengths)
            summary["smallest_gap"] = min(gap_lengths)

        else:

            summary["largest_gap"] = 0.0
            summary["smallest_gap"] = 0.0

        return {
            "chunks": chunks,
            "gaps": gaps,
            "summary": summary
        }

    def filter_chunks(
        self,
        chunks,
        min_length
    ):
        """
        Filter chunks by minimum number of points.

        Parameters
        ----------
        chunks : list
            Chunk list returned by run().

        min_length : int
            Minimum acceptable chunk length.

        Returns
        -------
        list
            Filtered chunk list.
        """

        return [
            chunk
            for chunk in chunks
            if chunk["length"] >= min_length
        ]