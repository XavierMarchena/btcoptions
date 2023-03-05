FROM node:12.20-alpine As builder

WORKDIR /usr/src/app

COPY package.json package-lock.json ./

RUN npm install

COPY . .

#RUN npm run build --prod
RUN npm install -g @angular/cli
#RUN ng build --deploy-url ./
#ng build --prod --base-href /btcoptions/
RUN ng build --base-href /btcoptions/

FROM nginx:1.15.8-alpine

#COPY --from=builder /usr/src/app/dist/btcoptions /usr/share/nginx/html/page/

COPY --from=builder /usr/src/app/dist/btcoptions /usr/share/nginx/html/page/btcoptions/

COPY default.conf /etc/nginx/conf.d/
