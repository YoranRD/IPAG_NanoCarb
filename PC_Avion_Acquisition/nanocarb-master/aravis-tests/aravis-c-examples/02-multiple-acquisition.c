/* SPDX-License-Identifier:Unlicense */

/* Aravis header */

#include <arv.h>

/* Standard headers */

#include <stdlib.h>
#include <stdio.h>
#include <time.h>

/*
 * Connect to the first available camera, then acquire 10 buffers.
 */

int
main (int argc, char **argv)
{
	ArvCamera *camera;
	GError *error = NULL;

	/* Connect to the first available camera */
	camera = arv_camera_new (NULL, &error);

	if (ARV_IS_CAMERA (camera)) {
		ArvStream *stream;

		printf ("Found camera '%s'\n", arv_camera_get_model_name (camera, NULL));

		/* Create the stream object without callback */
		stream = arv_camera_create_stream (camera, NULL, NULL, &error);
		if (ARV_IS_STREAM (stream)) {
			int i;
			size_t payload;

			/* Retrive the payload size for buffer creation */
			payload = arv_camera_get_payload (camera, &error);
			if (error == NULL) {
				/* Insert some buffers in the stream buffer pool */
				for (i = 0; i < 5; i++)
					arv_stream_push_buffer (stream, arv_buffer_new (payload, NULL));
			}

			if (error == NULL)
				/* Start the acquisition */
				arv_camera_start_acquisition (camera, &error);

			if (error == NULL) {
				int n_file = 1; 
                char fileName[20];
				FILE * file;
				/* Retrieve 10 buffers */
				for (i = 0; i < 10; i++) {
					ArvBuffer *buffer;

					buffer = arv_stream_pop_buffer (stream);
					if (ARV_IS_BUFFER (buffer)) {
						/* Display some informations about the retrieved buffer */
						printf ("Acquired %d×%d buffer\n",
							arv_buffer_get_image_width (buffer),
							arv_buffer_get_image_height (buffer));


						size_t size;
                        const char* data = arv_buffer_get_data(buffer, &size);

						/* Get Timestamp and write it */
						struct timespec now;
						timespec_get(&now, TIME_UTC);						
						
						sprintf(fileName, "video/test_%d.raw", n_file);

						file = fopen(fileName, "wb");

						struct tm * time = gmtime(&now.tv_sec);

						int year = time->tm_year+1900;
						int month = time->tm_mon+1;
						int day = time->tm_mday;
						int hour = time->tm_hour;
						int min = time->tm_min;
						int sec = time->tm_sec;
						int msec = now.tv_nsec/1.0e6;


						putw(year, file);
						fseek(file, -2, SEEK_END);
						putw(month, file);
						fseek(file, -2, SEEK_END);
						putw(day, file);
						fseek(file, -2, SEEK_END);
						putw(hour, file);
						fseek(file, -2, SEEK_END);
						putw(min, file);
						fseek(file, -2, SEEK_END);
						putw(sec, file);
						fseek(file, -2, SEEK_END);
						putw(msec, file);

						fseek(file, -2, SEEK_END);
						fwrite(data, size, 1, file);


						fclose(file);


						++n_file;
						

					
						/* Don't destroy the buffer, but put it back into the buffer pool */
						arv_stream_push_buffer (stream, buffer);
					}
				}

				gint in, out;
				arv_stream_get_n_buffers(stream, &in, &out);

				printf("%d input buffers\n%d output buffers\n", in, out);
			}

			if (error == NULL)
				/* Stop the acquisition */
				arv_camera_stop_acquisition (camera, &error);

			/* Destroy the stream object */
			g_clear_object (&stream);
		}

		/* Destroy the camera instance */
		g_clear_object (&camera);
	}

	if (error != NULL) {
		/* En error happened, display the correspdonding message */
		printf ("Error: %s\n", error->message);
		return EXIT_FAILURE;
	}

	return EXIT_SUCCESS;
}

