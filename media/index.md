# Media Processing

FFmpeg commands and tools for video/audio processing on Ubuntu.

## Files

### mmpeg.txt

**FFmpeg command examples** for video and audio processing.

**Features covered:**
- **Trim and concatenate videos** - Cut specific segments and combine them
- **Reduce file size** - Compress videos using H.265/HEVC codec
- **Extract segments** - Remove unwanted parts from videos
- **Audio synchronization** - Keep audio in sync when trimming

**Common operations:**

**Reduce quality and file size:**
```bash
ffmpeg -i input.mp4 -vcodec libx265 -crf 24 output.mp4
```

**Trim video (example: 0-1:55 and 2:14 onwards):**
```bash
ffmpeg -i input.mp4 -filter_complex \
"[0:v]trim=duration=115[av];[0:a]atrim=duration=115[aa];\
 [0:a]atrim=start=134,asetpts=PTS-STARTPTS[da];\
 [0:v]trim=start=134,setpts=PTS-STARTPTS[dv];\
 [av][dv]concat[outv];[aa][da]concat=v=0:a=1[outa]" \
-map [outv] -map [outa] output.mp4
```

**Cut out middle section (keep 0-30s, 40-50s, 80s-end):**
```bash
ffmpeg -i input.ts -filter_complex \
"[0:v]trim=duration=30[av];[0:a]atrim=duration=30[aa];\
 [0:v]trim=start=40:end=50,setpts=PTS-STARTPTS[bv];\
 [0:a]atrim=start=40:end=50,asetpts=PTS-STARTPTS[ba];\
 [av][bv]concat[cv];[aa][ba]concat=v=0:a=1[ca];\
 [0:v]trim=start=80,setpts=PTS-STARTPTS[dv];\
 [0:a]atrim=start=80,asetpts=PTS-STARTPTS[da];\
 [cv][dv]concat[outv];[ca][da]concat=v=0:a=1[outa]" \
-map [outv] -map [outa] output.ts
```

**Key concepts:**
- `trim` - Cuts video segments
- `atrim` - Cuts audio segments  
- `setpts/asetpts` - Resets timestamps after cutting
- `concat` - Joins multiple segments
- `-crf` - Quality level (lower = better quality, larger file)
