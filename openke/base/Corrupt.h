#ifndef CORRUPT_H
#define CORRUPT_H
#include "Random.h"
#include "Triple.h"
#include "Reader.h"

INT find_id(string r){
	INT count = 0, flag = 0;
	INT id;
	while (count != -1)
	{
		string *ptrToString = rel2id.keyValue[count].key;
		string actualString = *ptrToString;

		if (flag == 0 && actualString == r)
		{
			long *ptrToLong = rel2id.keyValue[count].value;
			long actualLong = *ptrToLong;
			id = actualLong;
			flag = 1;
		}
		if(flag==1)
			count = -1;
	}
	return id;
}

INT corrupt_head(INT id, INT h, INT r,INT t, bool filter_flag = true) {
	INT lef, rig, mid, ll, rr;
	INT rel_id, brod_id;

	rel_id = find_id("http://www.w3.org/2004/02/skos/core#related");
	brod_id = find_id("http://www.w3.org/2004/02/skos/core#broader");
	
    if (r == rel_id || r == brod_id ) { 
        return t;
    }
  
    else{
	if (not filter_flag) {
		INT tmp = rand_max(id, entityTotal - 1);
		if (tmp < h)
			return tmp;
		else
			return tmp + 1;
	}
	lef = lefHead[h] - 1;
	rig = rigHead[h];
	while (lef + 1 < rig) {
		mid = (lef + rig) >> 1;
		if (trainHead[mid].r >= r) rig = mid; else
		lef = mid;
	}
	ll = rig;
	lef = lefHead[h];
	rig = rigHead[h] + 1;
	while (lef + 1 < rig) {
		mid = (lef + rig) >> 1;
		if (trainHead[mid].r <= r) lef = mid; else
		rig = mid;
	}
	rr = lef;
	INT tmp = rand_max(id, entityTotal - (rr - ll + 1));
	if (tmp < trainHead[ll].t) return tmp;
	if (tmp > trainHead[rr].t - rr + ll - 1) return tmp + rr - ll + 1;
	lef = ll, rig = rr + 1;
	while (lef + 1 < rig) {
		mid = (lef + rig) >> 1;
		if (trainHead[mid].t - mid + ll - 1 < tmp)
			lef = mid;
		else 
			rig = mid;
	}
	return tmp + lef - ll + 1;
}
}

INT corrupt_tail(INT id, INT t, INT r, INT h, bool filter_flag = true) {
	INT lef, rig, mid, ll, rr;
	INT rel_id, brod_id;

	rel_id = find_id("http://www.w3.org/2004/02/skos/core#related");
	brod_id = find_id("http://www.w3.org/2004/02/skos/core#broader");
	
    if (r == rel_id  || r == brod_id) { 
        return h;
    }
    else{
	if (not filter_flag) {
		INT tmp = rand_max(id, entityTotal - 1);
		if (tmp < t)
			return tmp;
		else
			return tmp + 1;
	}
	lef = lefTail[t] - 1;
	rig = rigTail[t];
	while (lef + 1 < rig) {
		mid = (lef + rig) >> 1;
		if (trainTail[mid].r >= r) rig = mid; else
		lef = mid;
	}
	ll = rig;
	lef = lefTail[t];
	rig = rigTail[t] + 1;
	while (lef + 1 < rig) {
		mid = (lef + rig) >> 1;
		if (trainTail[mid].r <= r) lef = mid; else
		rig = mid;
	}
	rr = lef;
	INT tmp = rand_max(id, entityTotal - (rr - ll + 1));
	if (tmp < trainTail[ll].h) return tmp;
	if (tmp > trainTail[rr].h - rr + ll - 1) return tmp + rr - ll + 1;
	lef = ll, rig = rr + 1;
	while (lef + 1 < rig) {
		mid = (lef + rig) >> 1;
		if (trainTail[mid].h - mid + ll - 1 < tmp)
			lef = mid;
		else 
			rig = mid;
	}
	return tmp + lef - ll + 1;
}
}


INT corrupt_rel(INT id, INT h, INT t, INT r, bool p = false, bool filter_flag = true) {
	INT lef, rig, mid, ll, rr, r_new;
	INT rel_id, brod_id;

	rel_id = find_id("http://www.w3.org/2004/02/skos/core#related");
	brod_id = find_id("http://www.w3.org/2004/02/skos/core#broader");
	
	if (r == rel_id ){
        r_new = brod_id;
        return r_new;
    } 
    else if (r == brod_id) { 
        r_new = rel_id;
        return r_new;
    }
    else{
	if (not filter_flag) {
		INT tmp = rand_max(id, relationTotal - 1);
		if (tmp < r)
			return tmp;
		else
			return tmp + 1;
	}
	lef = lefRel[h] - 1;
	rig = rigRel[h];
	while (lef + 1 < rig) {
		mid = (lef + rig) >> 1;
		if (trainRel[mid].t >= t) rig = mid; else
		lef = mid;
	}
	ll = rig;
	lef = lefRel[h];
	rig = rigRel[h] + 1;
	while (lef + 1 < rig) {
		mid = (lef + rig) >> 1;
		if (trainRel[mid].t <= t) lef = mid; else
		rig = mid;
	}
	rr = lef;
	INT tmp;
	if(p == false) {	
		tmp = rand_max(id, relationTotal - (rr - ll + 1));
	}
	else {
		INT start = r * (relationTotal - 1);
		REAL sum = 1;
		bool *record = (bool *)calloc(relationTotal - 1, sizeof(bool));
		for (INT i = ll; i <= rr; ++i){
			if (trainRel[i].r > r){
				sum -= prob[start + trainRel[i].r-1];
				record[trainRel[i].r-1] = true;
			}
			else if (trainRel[i].r < r){
				sum -= prob[start + trainRel[i].r];
				record[trainRel[i].r] = true;
			}
		}		
		REAL *prob_tmp = (REAL *)calloc(relationTotal-(rr-ll+1), sizeof(REAL));
		INT cnt = 0;
		REAL rec = 0;
		for (INT i = start; i < start + relationTotal - 1; ++i) {
			if (record[i-start])
				continue;
			rec += prob[i] / sum;
			prob_tmp[cnt++] = rec;
		}
		REAL m = rand_max(id, 10000) / 10000.0;
		lef = 0;
		rig = cnt - 1;
		while (lef < rig) {
			mid = (lef + rig) >> 1;
			if (prob_tmp[mid] < m) 
				lef = mid + 1; 
			else
				rig = mid;
		}
		tmp = rig;
		free(prob_tmp);
		free(record);
	}
	if (tmp < trainRel[ll].r) return tmp;
	if (tmp > trainRel[rr].r - rr + ll - 1) return tmp + rr - ll + 1;
	lef = ll, rig = rr + 1;
	while (lef + 1 < rig) {
		mid = (lef + rig) >> 1;
		if (trainRel[mid].r - mid + ll - 1 < tmp)
			lef = mid;
		else 
			rig = mid;
	}
	return tmp + lef - ll + 1;
}
}


bool _find(INT h, INT t, INT r) {
    INT lef = 0;
    INT rig = tripleTotal - 1;
    INT mid;
    while (lef + 1 < rig) {
        INT mid = (lef + rig) >> 1;
        if ((tripleList[mid]. h < h) || (tripleList[mid]. h == h && tripleList[mid]. r < r) || (tripleList[mid]. h == h && tripleList[mid]. r == r && tripleList[mid]. t < t)) lef = mid; else rig = mid;
    }
    if (tripleList[lef].h == h && tripleList[lef].r == r && tripleList[lef].t == t) return true;
    if (tripleList[rig].h == h && tripleList[rig].r == r && tripleList[rig].t == t) return true;
    return false;
}

/*
INT corrupt(INT h, INT r){
	INT ll = tail_lef[r];
	INT rr = tail_rig[r];
	INT loop = 0;
	INT t;
	int rel_id = rel2id["http://www.w3.org/2004/02/skos/core#related"];
	int brod_id = rel2id["http://www.w3.org/2004/02/skos/core#broader"];
    if (r == rel_id || r == brod_id) { 
        return corrupt_head(0, h, r,t);
    }
    else{
	while(true) {
		t = tail_type[rand(ll, rr)];
		if (not _find(h, t, r)) {
			return t;
		} else {
			loop ++;
			if (loop >= 1000) {
				return corrupt_head(0, h, r,t);
			}
		} 
	}
}
}
*/
#endif
