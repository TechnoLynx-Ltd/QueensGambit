import { init_hand_tracking } from "./handpose.js";
import { renderResult } from "./handpose.js"
import { camera } from "./handpose.js"

let xStepSize, yStepSize;
let hands;
let prev_is_click=false;
export async function init_hand_pose_interface() {
	await init_hand_tracking()

	xStepSize = camera.video.width / 8;
  	yStepSize = camera.video.height / 8;
  	
}

export async function detect_hand() {
	hands = await renderResult();
	if (hands.length > 0) {
		var table_coord = calc_table_coord(hands[0]);
		is_click(hands[0])
        return {'is_hand_present': true, 'is_click': is_click(hands[0]), 'position': table_coord};
    }
    else {
    	return {'is_hand_present': false, 'is_click': false, 'position': null};	
    }
}

function is_click(hand) {
	// click if dip is lower than pip
	var click = hand["keypoints"][6]['y'] <hand["keypoints"][7]['y'];
	var result = !prev_is_click && hand["keypoints"][6]['y'] <hand["keypoints"][7]['y']
	prev_is_click = click;
	if(result) {
		console.log('IS_CLICK')
	}
	return result;
	
}

function calc_table_coord(hand) {
	var x_coord = hand["keypoints"][0]['x'];
	var y_coord = hand["keypoints"][0]['y'];

	if(x_coord < 0) {
      x_coord = 0
    }
    if(y_coord < 0) {
      y_coord = 0
    }
    x_coord = camera.video.width - x_coord;
    x_coord = Math.floor(x_coord / xStepSize);
    y_coord = Math.floor(y_coord / yStepSize);

    if(x_coord > 7) 
    {
    	x_coord = 7;
    }
    if(y_coord > 7)
    {
    	y_coord = 7;
    }
    if(x_coord < 0) 
    {
    	x_coord = 0;
    }
    if(y_coord < 0)
    {
    	y_coord = 0;
    }
    return [x_coord, y_coord]
}