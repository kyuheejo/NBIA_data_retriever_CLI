package main

import (
	"bytes"
	"io/ioutil"
	"net/http"
	"strconv"
	"strings"
	"testing"

	"github.com/rs/zerolog/log"
)

func TestDownload(t *testing.T) {

	info := &FileInfo{URL: "https://public.cancerimagingarchive.net/nbia-download/servlet/DownloadServletV3?numberOfSeries=1&series1=1.2.276.0.7230010.3.1.3.8323329.16721.1440002299.978656"}

	resp, err := http.Post(info.URL, "application/x-www-form-urlencoded; charset=ISO-8859-1", bytes.NewReader([]byte("")))

	if err != nil {
		t.Fatal(err)
	}

	content, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		t.Fatal(err)
	}

	data := strings.Split(string(content), "|")

	if len(data) < 11 {
		log.Error().Msgf("%v less than 11 elements", data)
	}

	info.Collection = data[0]
	info.PatientID = data[1]
	info.StudyUID = data[2]
	info.SeriesUID = data[3]

	if size, err := strconv.ParseInt(data[6], 10, 64); err != nil {
		log.Error().Msgf("%v", err)
	} else {
		info.Size = int64(size)
	}

	info.Date = data[11]

	err = info.Download("", "username", "")
	t.Fatal(err)
}
