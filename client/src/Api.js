/*
 * Copyright (c) 2016-2022 Tom Keffer <tkeffer@gmail.com>
 *
 * See the file LICENSE for your full rights.
 */

import io from "socket.io-client";

export function getPackets(measurement, tags, start, stop, aggregation) {
  const { platform, stream } = tags;

  const url = `http://${window.location.host}/api/v1/measurements/${measurement}/packets`;
  let params = `?start=${start}`;
  if (stop) params += `&stop=${stop}`;
  if (aggregation) params += `&group=${aggregation}`;
  if (platform) params += `&platform=${platform}`;
  if (stream) params += `&stream=${stream}`;

  const fullUrl = url + params;

  // TODO: Should probably add a timeout
  return fetch(fullUrl).then(response => {
    if (!response.ok) {
      return Promise.reject(new Error(response.statusText));
    }
    return response.json();
  });
}

export function getStats(measurement, tags, span) {
  const { platform, stream } = tags;

  const url = `http://${window.location.host}/api/v1/measurements/${measurement}/stats`;
  let params = `?span=${span}`;
  if (platform) params += `&platform=${platform}`;
  if (stream) params += `&stream=${stream}`;

  const fullUrl = url + params;

  return fetch(fullUrl).then(response => {
    if (!response.ok) return Promise.reject(new Error(response.statusText));
    return response.json();
  });
}

export function subscribe(measurement, tags, callback) {
  const socket = io();
  socket.on("/" + measurement, callback);
  return socket;
}

export function unsubscribe(socket) {
  socket.close();
}

export function getAbout() {
  const url = `http://${window.location.host}/api/v1/about`;

  return fetch(url).then(response => {
    if (!response.ok) return Promise.reject(new Error(response.statusText));
    return response.json();
  });
}
