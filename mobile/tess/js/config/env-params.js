/**
 * SLAC 2019
 *
 * Created by: Jonathan G.
 *
 * Enviroment specific configuration parameters
 */

const dev = {
	baseURL: 'https://api.dev.tess.com',
}

const rc = {
	baseURL: 'https://api.rc.tess.com',
}

const prod = {
	baseURL: 'https://api.prod.tess.com',
}

const hf = {
	baseURL: 'https://api.hf.tess.com',
}

const debug = {
    baseURL: 'http://localhost:8000',
}

export const environments = { dev, rc, prod, hf, debug }
