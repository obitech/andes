# Overview

## Authentication
Method | Endpoint | Comments
---|---|---
POST|[/register](endpoints/user/register/post.md)|Registers new user
POST|[/auth](endpoints/user/auth/post.md)|Authenticates user

## Blueprints
Method | Endpoint | Comments
---|---|---
GET|[/blueprints](endpoints/blueprints/get.md)|Retrieves list of blueprints
GET|[/blueprints/<_id>](endpoints/blueprints/id/get.md)|Retrieves single blueprint
DELETE|[/blueprints/<_id>](endpoints/blueprints/id/delete.md)|Deletes a single blueprint
POST|[/blueprints/create](endpoints/blueprints/create/post.md)|Creates a new blueprint
PUT|[/blueprints/create](endpoints/blueprints/create/put.md)|Creates or updates a blueprint

## Services
Method | Endpoint | Comments
---|---|---
GET|[/services](endpoints/services/get.md)|Retrieves list of services
GET|[/services/<_id>](endpoints/services/id/get.md)|Retrieves single services
DELETE|[/services/<_id>](endpoints/services/id/delete.md)|Deletes single service
POST|[/services/create](endpoints/services/create/post.md)|Creates a new service
PUT|[/services/create](endpoints/services/create/put.md)|Creates or updates a service

## Stacks
Method | Endpoint | Comments
---|---|---
GET|[/stacks](endpoints/stacks/get.md)|Retrieves list of stacks
GET|[/stacks/<_id>](endpoints/stacks/id/get.md)|Retrieves single stacks
DELETE|[/stacks/<_id>](endpoints/stacks/id/delete.md)|Deletes single service
POST|[/stacks/<_id>/apply](endpoints/stacks/id/apply/post.md)|Applies a stack and saves config files to disk
POST|[/stacks/create](endpoints/stacks/create/post.md)|Creates a new stack
PUT|[/stacks/create](endpoints/stacks/create/put.md)|Creates or updates a stack