/* Headers */

#include <glib.h>
#include <arv.h>

/* Standard headers */

#include <stdlib.h>
#include <stdio.h>
#include <time.h>

int
main(int argc, char ** argv)
{
    ArvCamera *camera;
    ArvBuffer *buffer;
    GError *error = NULL;

    /* Connect to the first available camera */
    camera = arv_camera_new(NULL, &error);

    if (ARV_IS_CAMERA(camera)) {
        printf("Found camera '%s'\n", arv_camera_get_model_name(camera, NULL));
    }

    /* Acquire single buffer */
	buffer = arv_camera_acquisition(camera, 0, &error);

	if (ARV_IS_BUFFER(buffer)) {
		printf("Acquired %dx%d buffer\n", arv_buffer_get_image_width(buffer), arv_buffer_get_image_height(buffer));
	
		size_t size;
		const char* data = arv_buffer_get_data(buffer, &size);
		g_file_set_contents("test_Mono14.raw", data, size, NULL);

	}
		
    g_clear_object(&buffer);
    g_clear_object(&camera);

    if (error != NULL) {
		/* En error happened, display the correspdonding message */
		printf ("Error: %s\n", error->message);
		return EXIT_FAILURE;
	}

	

	return EXIT_SUCCESS;
}