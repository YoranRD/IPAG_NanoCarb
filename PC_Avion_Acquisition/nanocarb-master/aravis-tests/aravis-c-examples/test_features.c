/* Aravis header */

#include <arv.h>

/* Standard headers */

#include <stdlib.h>
#include <stdio.h>

/*
 * Connect to the first available camera, then acquire a single buffer.
 */

int
main (int argc, char **argv)
{
	ArvCamera *camera;
	GError *error = NULL;
    ArvDevice *device;

    /* Connect to the first available camera */
	camera = arv_camera_new (NULL, &error);

    device = arv_camera_get_device(camera);

    float FPS;

    FPS = arv_device_get_float_feature_value(device, "FrameRate", &error);
    printf("FPS : %f\n", FPS);

    arv_device_set_float_feature_value(device, "FrameRate", 20.0, &error);

    FPS = arv_device_get_float_feature_value(device, "FrameRate", &error);
    printf("FPS : %f\n", FPS);

    
    float fpsMax;
    fpsMax = arv_device_get_float_feature_value(device, "FrameRateMax", &error);

    printf("FPS Max : %f\n", fpsMax);

    int flipV;
    flipV = arv_device_get_boolean_feature_value(device, "FlipVertical", &error);

    printf("Flip vertical : %d\n", flipV);
    arv_device_set_boolean_feature_value(device, "FlipVertical", 0, &error);

    


    g_clear_object(&camera);

    if (error != NULL) {
		/* En error happened, display the correspdonding message */
		printf ("Error: %s\n", error->message);
		return EXIT_FAILURE;
	}

    return EXIT_SUCCESS;
}