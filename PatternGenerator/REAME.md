Generates pattern. Run `generate.py` file using python3. 

```
(Py36) [dilawars@DMO PatternGenerator (master)]$ ./generate.py -h
usage: generate.py [-h] [--ROI ROI] [--num-patterns NUM_PATTERNS]
                   [--num-rect NUM_RECT | --loc LOC]
                   [--size-pattern SIZE_PATTERN] [--noise NOISE] [--seed SEED]

Generate PNG file for projector.

optional arguments:
  -h, --help            show this help message and exit
  --ROI ROI, -r ROI     Size of ROI in pixels.
  --num-patterns NUM_PATTERNS, -np NUM_PATTERNS
                        Number of patterns to generate.
  --num-rect NUM_RECT, -nr NUM_RECT
                        Number of rectangles to put on an image.
  --loc LOC, -l LOC     location of rectangles e.g., x1:y1,x2:y2 etc.
  --size-pattern SIZE_PATTERN, -sp SIZE_PATTERN
                        Size of each rectangle.
  --noise NOISE, -n NOISE
                        Gaussian noise (std) in each rectangle location.Only
                        when position of each rectangle is given
  --seed SEED, -s SEED  random seed.
(Py36) [dilawars@DMO PatternGenerator (master)]$ 
```
